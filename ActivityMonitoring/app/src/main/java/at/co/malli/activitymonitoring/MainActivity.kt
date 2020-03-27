package at.co.malli.activitymonitoring

import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.util.Log
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.util.*

class MainActivity : AppCompatActivity(), SensorEventListener {

    companion object {
        private val TAG: String? = MainActivity::class.simpleName
        const val RECORD_DELAY_S: Long = 5 //time in s until sensor values are saved in list
    }

    private val sensorDataList = LinkedList<SensorValue>()
    private lateinit var sm: SensorManager
    private var recordPressedTime: Long = Long.MAX_VALUE

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sm = getSystemService(SENSOR_SERVICE) as SensorManager
    }

    fun recordPressed(view: View) {
        Log.v(TAG, "recordPressed")
        val accelerometer = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        sm.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_NORMAL)
        recordPressedTime = System.nanoTime()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        if(sensor != null)
            Log.d(TAG, "Accuracy of sensor " + sensor.name + " changed to $accuracy")
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event != null) {
            if (recordPressedTime == Long.MAX_VALUE)
                recordPressedTime = event.timestamp //set to first timestamp
            if (event.timestamp > recordPressedTime + RECORD_DELAY_S * 1000 * 1000 * 1000) {
                sensorDataList.add(
                    SensorValue(
                        event.values[0], event.values[1], event.values[2], event.timestamp
                    )
                )
            }
        }
    }

    fun stopPressed(view: View) {
        sm.unregisterListener(this)
        Log.v(TAG, "stopPressed")

        if (sensorDataList.isEmpty()) {
            Log.v(TAG, "List empty! Will not write anything!")
            return
        }

        val lastTimestamp = sensorDataList.last.timestamp
        val path = File(this.filesDir, "$lastTimestamp.csv")
        val fOutStream = OutputStreamWriter(FileOutputStream(path))
        Log.v(TAG, "Opened file for writing with name $lastTimestamp.csv")
        Log.v(TAG, "sensorDataList has ${sensorDataList.size} entries")
        var cnt = 0
        for (data in sensorDataList) {
            if (data.timestamp < lastTimestamp - RECORD_DELAY_S * 1000 * 1000 * 1000) {
                //do not save data of last x seconds...
                fOutStream.write("${data.x}, ${data.y}, ${data.z}, ${data.timestamp}")
                cnt++
            }
        }
        fOutStream.flush()
        fOutStream.close()
        Log.v(TAG, "Finished writing $cnt entries.")
    }

}
