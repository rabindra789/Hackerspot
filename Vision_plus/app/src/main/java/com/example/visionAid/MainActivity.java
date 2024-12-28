package com.example.visionAid;

import android.Manifest;
import android.content.pm.PackageManager;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.widget.ImageButton;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.Camera;
import androidx.camera.core.CameraControl;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;

import com.google.common.util.concurrent.ListenableFuture;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Locale;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    private static final String BACKEND_URL = "https://correct-cricket-busy.ngrok-free.app/api/detect";
    private PreviewView previewView;
    private ImageCapture imageCapture;
    private Camera camera;
    private ExecutorService cameraExecutor;
    private MediaPlayer mediaPlayer;
    private TextToSpeech textToSpeech;
    private ImageButton flashButton;
    private ImageButton captureButton;
    private ImageButton flipCameraButton;
    private boolean isFlashOn = false;
    private boolean isUsingBackCamera = true; // Track which camera is currently in use

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        previewView = findViewById(R.id.cameraPreview);
        captureButton = findViewById(R.id.capture);
        flipCameraButton = findViewById(R.id.flipCamera);
        flashButton = findViewById(R.id.toggleFlash);

        captureButton.setOnClickListener(v -> captureImage());
        flipCameraButton.setOnClickListener(v -> flipCamera());
        flashButton.setOnClickListener(v -> toggleFlash());

        // Check for camera permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
            startCamera();
        } else {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, 101);
        }

        // Initialize TextToSpeech
        textToSpeech = new TextToSpeech(this, status -> {
            if (status == TextToSpeech.SUCCESS) {
                int result = textToSpeech.setLanguage(Locale.US);
                if (result == TextToSpeech.LANG_MISSING_DATA ||
                        result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Log.e("TTS", "Language not supported");
                }
            } else {
                Log.e("TTS", "Initialization failed");
            }
        });
    }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> cameraProviderFuture = ProcessCameraProvider.getInstance(this);
        cameraProviderFuture.addListener(() -> {
            try {
                ProcessCameraProvider cameraProvider = cameraProviderFuture.get();
                Preview preview = new Preview.Builder().build();
                imageCapture = new ImageCapture.Builder().build();

                // Select the camera based on the current state
                CameraSelector cameraSelector = new CameraSelector.Builder()
                        .requireLensFacing(isUsingBackCamera ? CameraSelector.LENS_FACING_BACK : CameraSelector.LENS_FACING_FRONT)
                        .build();

                cameraProvider.unbindAll();
                camera = cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture);
                preview.setSurfaceProvider(previewView.getSurfaceProvider());
            } catch (ExecutionException | InterruptedException e) {
                e.printStackTrace();
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void captureImage() {
        if (imageCapture == null) return;

        File file = new File(getExternalFilesDir(null), "image.jpg");
        ImageCapture.OutputFileOptions outputOptions = new ImageCapture.OutputFileOptions.Builder(file).build();

        imageCapture.takePicture(outputOptions, Executors.newSingleThreadExecutor(),
                new ImageCapture.OnImageSavedCallback() {
                    @Override
                    public void onImageSaved(@ NonNull ImageCapture.OutputFileResults outputFileResults) {
                        runOnUiThread(() -> Toast.makeText(MainActivity.this, "Image captured.", Toast.LENGTH_SHORT).show());
                        uploadImageToBackend(file);
                    }

                    @Override
                    public void onError(@NonNull ImageCaptureException exception) {
                        runOnUiThread(() -> Toast.makeText(MainActivity.this, "Error capturing image.", Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void uploadImageToBackend(File imageFile) {
        OkHttpClient client = new OkHttpClient();
        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("image", imageFile.getName(),
                        RequestBody.create(imageFile, MediaType.parse("image/jpeg")))
                .build();

        Request request = new Request.Builder()
                .url(BACKEND_URL)
                .post(requestBody)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "Failed to upload image.", Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                if (response.isSuccessful()) {
                    String responseBody = response.body().string();

                    try {
                        JSONObject jsonResponse = new JSONObject(responseBody);
                        JSONArray detections = jsonResponse.getJSONArray("detections");

                        HashMap<String, Integer> objectCountMap = new HashMap<>();
                        for (int i = 0; i < detections.length(); i++) {
                            JSONObject detection = detections.getJSONObject(i);
                            String className = detection.getString("class_name");
                            objectCountMap.put(className, objectCountMap.getOrDefault(className, 0) + 1);
                        }

                        StringBuilder detectedObjects = new StringBuilder();
                        for (String key : objectCountMap.keySet()) {
                            int count = objectCountMap.get(key);
                            detectedObjects.append(count).append(" ").append(key).append(", ");
                        }

                        // Remove trailing comma and space
                        if (detectedObjects.length() > 2) {
                            detectedObjects.delete(detectedObjects.length() - 2, detectedObjects.length());
                        }

                        // Speak the detected objects
                        textToSpeech.speak(detectedObjects.toString(), TextToSpeech.QUEUE_FLUSH, null, null);

                    } catch (JSONException e) {
                        e.printStackTrace();
                        runOnUiThread(() -> Toast.makeText(MainActivity.this, "Error parsing JSON response", Toast.LENGTH_SHORT).show());
                    }
                } else {
                    runOnUiThread(() -> Toast.makeText(MainActivity.this, "Error in backend response.", Toast.LENGTH_SHORT).show());
                }
            }
        });
    }

    private void toggleFlash() {
        if (camera != null) {
            CameraControl cameraControl = camera.getCameraControl();
            try {
                if (isFlashOn) {
                    cameraControl.enableTorch(false);
                    flashButton.setImageResource(R.drawable.ic_flash); // Change to flash off icon
                } else {
                    cameraControl.enableTorch(true);
                    flashButton.setImageResource(R.drawable.ic_flash); // Change to flash on icon
                }
                isFlashOn = !isFlashOn;
            } catch (Exception e) {
                Log.e("FlashToggle", "Error toggling flash", e);
                Toast.makeText(this, "Error toggling flash", Toast.LENGTH_SHORT).show();
            }
        } else {
            Toast.makeText(this, "Camera not initialized", Toast.LENGTH_SHORT).show();
        }
    }

    private void flipCamera() {
        isUsingBackCamera = !isUsingBackCamera; // Toggle the camera state
        startCamera(); // Restart the camera with the new state
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 101 && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startCamera();
        } else {
            Toast.makeText(this, "Camera permission required.", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onDestroy() {
        // Shutdown TextToSpeech when the activity is destroyed
        if (textToSpeech != null) {
            textToSpeech.stop();
            textToSpeech.shutdown();
        }
        super.onDestroy();
    }
}