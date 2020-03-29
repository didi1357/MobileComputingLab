package at.co.malli.activitymonitoring

import android.Manifest
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.util.*
import at.co.malli.activitymonitoring.R


class MainActivity : AppCompatActivity(), SensorEventListener {

    companion object {
        private val TAG: String? = MainActivity::class.simpleName
        const val RECORD_DELAY_S: Long = 5 //time in s until sensor values are saved in list
        val sensorDataList = LinkedList<SensorValue>() //static to survive orientation chg.

        const val STATE_STOPPED = 0
        const val STATE_RECORDING = 1
        var currentState: Int = STATE_STOPPED

        const val REQUEST_EXTERNAL_STORAGE_PERMISSION = 1
        const val MY_SENSORTYPE_ACC = 0
        const val MY_SENSORTYPE_ROT = 1
    }

    private lateinit var sm: SensorManager
    private var recordPressedTime: Long = Long.MAX_VALUE

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sm = getSystemService(SENSOR_SERVICE) as SensorManager

        if (checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
            == PackageManager.PERMISSION_GRANTED
        ) {
            Log.v(TAG, "External storage permission is granted.");
        } else {
            Log.v(TAG, "Need to request external storage permission.")

            ActivityCompat.requestPermissions(
                this,
                arrayOf( Manifest.permission.WRITE_EXTERNAL_STORAGE),
                REQUEST_EXTERNAL_STORAGE_PERMISSION
            );
        }

        applyState(null)
    }

    override fun onRequestPermissionsResult(requestCode: Int,
                                            permissions: Array<String>, grantResults: IntArray) {
        when (requestCode) {
            REQUEST_EXTERNAL_STORAGE_PERMISSION -> {
                // If request is cancelled, the result arrays are empty.
                if ((grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED)) {
                    // permission was granted
                    Log.v(TAG, "External storage permission was granted right now!")
                } else {
                    // permission denied
                    Log.v(TAG, "Need to request external storage permission AGAIN.")
                    ActivityCompat.requestPermissions(
                        this,
                        arrayOf( Manifest.permission.WRITE_EXTERNAL_STORAGE),
                        REQUEST_EXTERNAL_STORAGE_PERMISSION
                    )
                }
            }
        }
    }

    fun applyState(new_state: Int?) {
        if (new_state != null)
            currentState = new_state

        val recordButton = findViewById<View>(R.id.recordButton) as Button
        val stopButton = findViewById<View>(R.id.stopButton) as Button
        if (currentState == STATE_RECORDING) {
            recordButton.isEnabled = false
            stopButton.isEnabled = true
        } else {
            recordButton.isEnabled = true
            stopButton.isEnabled = false
        }

    }

    fun recordPressed(view: View) {
        Log.v(TAG, "recordPressed")
        val accelerometer = sm.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)
        val rotation = sm.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
        sm.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST)
        sm.registerListener(this, rotation, SensorManager.SENSOR_DELAY_FASTEST)
        applyState(STATE_RECORDING)
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        if (sensor != null)
            Log.d(TAG, "Accuracy of sensor " + sensor.name + " changed to $accuracy")
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event != null) {
            if (recordPressedTime == Long.MAX_VALUE)
                recordPressedTime = event.timestamp //set to first timestamp
            if (event.timestamp > recordPressedTime + RECORD_DELAY_S * 1000 * 1000 * 1000) {
                var type = -1
                if(event.sensor.type == Sensor.TYPE_LINEAR_ACCELERATION)
                    type = MY_SENSORTYPE_ACC
                else if(event.sensor.type == Sensor.TYPE_ROTATION_VECTOR)
                    type = MY_SENSORTYPE_ROT
                sensorDataList.add(
                    SensorValue(
                        type, event.values[0], event.values[1], event.values[2], event.timestamp
                    )
                )
            }
        }
    }

    fun stopPressed(view: View) {
        sm.unregisterListener(this)
        applyState(STATE_STOPPED)
        Log.v(TAG, "stopPressed")

        if (sensorDataList.isEmpty()) {
            Log.v(TAG, "List empty! Will not write anything!")
            return
        }

        val lastTimestamp = sensorDataList.last.timestamp
        val path = File(getExternalFilesDir(null), "$lastTimestamp.csv")
        val fOutStream = OutputStreamWriter(FileOutputStream(path))
        Log.v(TAG, "Opened file for writing: $path")
        Log.v(TAG, "sensorDataList has ${sensorDataList.size} entries")
        var cnt = 0
        for (data in sensorDataList) {
            if (data.timestamp < lastTimestamp - RECORD_DELAY_S * 1000 * 1000 * 1000) {
                //do not save data of last x seconds...
                val str = "${data.type}, ${data.x}, ${data.y}, ${data.z}, ${data.timestamp}\n"
                fOutStream.write(str)
                cnt++
            }
        }
        fOutStream.flush()
        fOutStream.close()
        Log.v(TAG, "Finished writing $cnt entries.")

        sensorDataList.clear()
        recordPressedTime = Long.MAX_VALUE
    }

}
