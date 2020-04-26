package at.co.malli.activitymonitoring

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.os.PowerManager
import android.util.Log
import android.view.View
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.util.*


class MainActivity : AppCompatActivity(), SensorEventListener {

    companion object {
        private val TAG: String? = MainActivity::class.simpleName
        val sensorDataList = LinkedList<SensorValue>() //static to survive orientation chg.

        const val STATE_STOPPED = 0
        const val STATE_RECORDING = 1
        var currentState: Int = STATE_STOPPED

        const val REQUEST_EXTERNAL_STORAGE_PERMISSION = 1
        const val MY_SENSORTYPE_ACC = 0
        const val MY_SENSORTYPE_ROT = 1
    }

    private lateinit var sm: SensorManager
    private lateinit var wakeLock: PowerManager.WakeLock

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
                arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE),
                REQUEST_EXTERNAL_STORAGE_PERMISSION
            );
        }

        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "MyApp::MyWakelockTag"
        )

        applyState(null)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>, grantResults: IntArray
    ) {
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
                        arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE),
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
        wakeLock.acquire()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        if (sensor != null)
            Log.d(TAG, "Accuracy of sensor " + sensor.name + " changed to $accuracy")
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event != null) {
            var type = -1
            if (event.sensor.type == Sensor.TYPE_LINEAR_ACCELERATION)
                type = MY_SENSORTYPE_ACC
            else if (event.sensor.type == Sensor.TYPE_ROTATION_VECTOR)
                type = MY_SENSORTYPE_ROT
            sensorDataList.add(
                SensorValue(
                    type, event.values[0], event.values[1], event.values[2], event.timestamp
                )
            )
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
        for (data in sensorDataList) {
            val str = "${data.type}, ${data.x}, ${data.y}, ${data.z}, ${data.timestamp}\n"
            fOutStream.write(str)
        }
        fOutStream.flush()
        fOutStream.close()
        Log.v(TAG, "sensorDataList had ${sensorDataList.size} entries.")

        sensorDataList.clear()
        wakeLock.release()
    }

}
