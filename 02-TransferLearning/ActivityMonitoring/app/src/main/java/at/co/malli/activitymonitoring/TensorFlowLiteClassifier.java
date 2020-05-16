package at.co.malli.activitymonitoring;

import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.List;

import org.tensorflow.lite.Interpreter;

import static at.co.malli.activitymonitoring.MainActivity.WINDOW_N;


public class TensorFlowLiteClassifier {

    private Interpreter tfLite;
    private String name;
    private List<String> labels;

    private static List<String> readLabels(AssetManager am, String fileName) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(am.open(fileName)));

        String line;
        List<String> labels = new ArrayList<>();
        while ((line = br.readLine()) != null) {
            labels.add(line);
        }

        br.close();
        return labels;
    }

    public static TensorFlowLiteClassifier create(AssetManager assetManager, String name,
                                              String modelPath, String labelFile) throws IOException {

        TensorFlowLiteClassifier c = new TensorFlowLiteClassifier();
        c.name = name;

        // read labels for label file
        c.labels = readLabels(assetManager, labelFile);

        // set its model path and where the raw asset files are
        c.tfLite = new Interpreter(loadModelFile(assetManager, modelPath));
        int numClasses = 10;

        return c;
    }

    public String name() {
        return name;
    }

    public float[] recognize(final float[] inputArray) {
        float [][][][] tfLiteFormattedArray = new float[1][WINDOW_N][3][1]; //3 sensors..
        for(int i=0; i<WINDOW_N;i++) {
            for (int j = 0; j < 3; j++) {
                tfLiteFormattedArray[0][i][j][0] = inputArray[(i * 3) + j];
            }
        }

        float[][] probabilityArrForTfLite = new float[1][labels.size()];
        float[] arrToReturn = new float[labels.size()];

        tfLite.run(tfLiteFormattedArray, probabilityArrForTfLite);

        for (int i = 0; i < labels.size(); ++i) {
            arrToReturn[i] = probabilityArrForTfLite[0][i];
        }

        return arrToReturn;
    }

    // memory-map the model file in assets
    private static MappedByteBuffer loadModelFile(AssetManager assets, String modelFilename)
            throws IOException {
        AssetFileDescriptor fileDescriptor = assets.openFd(modelFilename);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }
}