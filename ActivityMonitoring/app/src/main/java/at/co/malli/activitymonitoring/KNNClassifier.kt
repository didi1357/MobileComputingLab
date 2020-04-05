package at.co.malli.activitymonitoring

import android.util.Log
import org.json.JSONObject
import java.io.InputStream
import java.io.InputStreamReader
import java.lang.Double.max
import java.lang.Double.min
import java.util.*
import kotlin.collections.ArrayList
import kotlin.math.pow
import kotlin.math.roundToInt
import kotlin.math.sqrt

class KNNClassifier(assetInputStream: InputStream) {

    companion object {
        private val TAG: String? = KNNClassifier::class.simpleName
        val CLASSES = arrayOf("downstairs", "upstairs", "sitting", "standing", "walking", "jogging")
    }

    val featureVectors: ArrayList<FeatureVector> = ArrayList()
    var kValue: Int = 0

    init {
        val reader = InputStreamReader(assetInputStream)
        val readText = reader.readText()
        reader.close()
        val jroot = JSONObject(readText)
        for (cntClass in CLASSES.indices) {
            var curClass = CLASSES[cntClass]
            var jVectors = jroot.getJSONArray(curClass)
            Log.d(TAG, "Got ${jVectors.length()} jvectors for $curClass")
            for (cntVectors in 0 until jVectors.length()) {
                var currentJvec = jVectors.getJSONArray(cntVectors)
                var currentVector = ArrayList<Double>()
                for (cnt_value in 0 until currentJvec.length()) {
                    currentVector.add(currentJvec.getDouble(cnt_value))
                }
                var currentFeatureVector = FeatureVector(currentVector, cntClass)
                featureVectors.add(currentFeatureVector)
            }
        }

        kValue = sqrt(featureVectors.size.toDouble()).roundToInt()
        Log.d(TAG, "n=${featureVectors.size} => k=$kValue")
    }

    fun calculateEuclideanDistance(trainVector: FeatureVector, testVector: FeatureVector): Double {
        var sumOfSquares = 0.0
        for (cnt_element in 0 until trainVector.values.size) {
            val difference = trainVector.values[cnt_element] - testVector.values[cnt_element]
            sumOfSquares += difference.pow(2.0)
        }
        return sqrt(sumOfSquares / trainVector.values.size.toDouble())
    }

    fun classify(testFeature: FeatureVector): ArrayList<Double> {
        var distances = ArrayList<DistanceClassPair>()
        for (cntFeat in 0 until featureVectors.size) {
            val currentDistance = calculateEuclideanDistance(featureVectors[cntFeat], testFeature)
            distances.add(DistanceClassPair(currentDistance, featureVectors[cntFeat].classNr))
        }
        distances.sort()
        var probabilities = ArrayList<Double>()
        for (cntClass in CLASSES.indices)
            probabilities.add(0.0)
        for (cntDist in 0 until kValue)
            probabilities[distances[cntDist].classNr] += 1.0
        for (cntClass in CLASSES.indices)
            probabilities[cntClass] = probabilities[cntClass] / CLASSES.size
        return probabilities
    }

    fun calculateFeatureVector(values: ArrayList<SensorValue>): FeatureVector {
        //https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
        var x_mean = values[0].x.toDouble()
        var y_mean = values[0].y.toDouble()
        var z_mean = values[0].z.toDouble()
        var x_min = values[0].x.toDouble()
        var y_min = values[0].y.toDouble()
        var z_min = values[0].z.toDouble()
        var x_max = values[0].x.toDouble()
        var y_max = values[0].y.toDouble()
        var z_max = values[0].z.toDouble()
        var x_std = 0.0
        var y_std = 0.0
        var z_std = 0.0
        var count = 0
        for (i in 1 until values.size) {
            x_min = min(x_min, values[i].x.toDouble())
            y_min = min(y_min, values[i].y.toDouble())
            z_min = min(z_min, values[i].z.toDouble())
            x_max = max(x_max, values[i].x.toDouble())
            y_max = max(y_max, values[i].y.toDouble())
            z_max = max(z_max, values[i].z.toDouble())
            count += 1
            var x_delta = values[i].x - x_mean
            var y_delta = values[i].y - y_mean
            var z_delta = values[i].z - z_mean
            x_mean += x_delta / count
            y_mean += y_delta / count
            z_mean += z_delta / count
            var x_delta2 = values[i].x - x_mean
            var y_delta2 = values[i].y - y_mean
            var z_delta2 = values[i].z - z_mean
            x_std += x_delta * x_delta2
            y_std += y_delta * y_delta2
            z_std += z_delta * z_delta2
        }
        x_std = Math.sqrt(x_std / (count - 1))
        y_std = Math.sqrt(y_std / (count - 1))
        z_std = Math.sqrt(z_std / (count - 1))
        val rv_data = ArrayList<Double>()
        rv_data.add(x_mean)
        rv_data.add(y_mean)
        rv_data.add(z_mean)
        rv_data.add(x_min)
        rv_data.add(y_min)
        rv_data.add(z_min)
        rv_data.add(x_max)
        rv_data.add(y_max)
        rv_data.add(z_max)
        rv_data.add(x_std)
        rv_data.add(y_std)
        rv_data.add(z_std)
        return FeatureVector(rv_data, FeatureVector.CLASSNR_UNDEFINED)
    }
}