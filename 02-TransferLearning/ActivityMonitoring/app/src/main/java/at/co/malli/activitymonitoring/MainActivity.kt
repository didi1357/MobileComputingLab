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
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.widget.Toolbar
import androidx.core.app.ActivityCompat
import androidx.drawerlayout.widget.DrawerLayout
import androidx.navigation.findNavController
import androidx.navigation.ui.AppBarConfiguration
import androidx.navigation.ui.navigateUp
import androidx.navigation.ui.setupActionBarWithNavController
import androidx.navigation.ui.setupWithNavController
import at.co.malli.activitymonitoring.ui.home.HomeFragment
import at.co.malli.activitymonitoring.ui.recording.RecordingFragment
import com.google.android.material.navigation.NavigationView
import java.io.File


class MainActivity : AppCompatActivity(), SensorEventListener {

    companion object {
        private val TAG: String? = MainActivity::class.simpleName
        var classifier: KNNClassifier? = null
        val sensorDataList = ArrayList<SensorValue>() //static to survive orientation chg.
        var externalFilesDir: File? = null

        const val REQUEST_EXTERNAL_STORAGE_PERMISSION = 1

        const val APPROX_SENS_VAL_DELAY_MS = 5.0
        const val DESIRED_WINDOW_MS = 1200.0f
        const val WINDOW_N: Int = (DESIRED_WINDOW_MS / APPROX_SENS_VAL_DELAY_MS).toInt()
    }

    private lateinit var sm: SensorManager
    private lateinit var wakeLock: PowerManager.WakeLock

    private lateinit var appBarConfiguration: AppBarConfiguration

    private lateinit var tlHandModel: TransferLearningModelWrapper
    private lateinit var tlPocketModel: TransferLearningModelWrapper
    private var tlModels = arrayOf(tlHandModel, tlPocketModel)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val toolbar: Toolbar = findViewById(R.id.toolbar)
        setSupportActionBar(toolbar)

        val drawerLayout: DrawerLayout = findViewById(R.id.drawer_layout)
        val navView: NavigationView = findViewById(R.id.nav_view)
        val navController = findNavController(R.id.nav_host_fragment)
        // Passing each menu ID as a set of Ids because each
        // menu should be considered as top level destinations.
        appBarConfiguration = AppBarConfiguration(
            setOf(
                R.id.nav_home, R.id.nav_recording
            ), drawerLayout
        )
        setupActionBarWithNavController(navController, appBarConfiguration)
        navView.setupWithNavController(navController)

        if (checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
            == PackageManager.PERMISSION_GRANTED
        ) {
            Log.v(TAG, "External storage permission is granted.")
        } else {
            Log.v(TAG, "Need to request external storage permission.")

            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.WRITE_EXTERNAL_STORAGE),
                REQUEST_EXTERNAL_STORAGE_PERMISSION
            );
        }

        externalFilesDir = getExternalFilesDir(null)

        classifier = KNNClassifier(applicationContext.assets.open("windowed.json"))

        tlHandModel = TransferLearningModelWrapper(applicationContext)
        tlPocketModel = TransferLearningModelWrapper(applicationContext)

        sm = getSystemService(SENSOR_SERVICE) as SensorManager
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "MyApp::MyWakelockTag"
        )
        val accelerometer = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        sm.registerListener(this, accelerometer, SensorManager.SENSOR_DELAY_FASTEST)
        wakeLock.acquire()
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp(appBarConfiguration) || super.onSupportNavigateUp()
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

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        if (sensor != null)
            Log.d(TAG, "Accuracy of sensor " + sensor.name + " changed to $accuracy")
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event != null) {
            sensorDataList.add(
                SensorValue(
                    event.values[0], event.values[1], event.values[2], event.timestamp
                )
            )
            if (sensorDataList.size > WINDOW_N) {
                when (RecordingFragment.currentState) {
                    RecordingFragment.STATE_STOPPED -> {
                        //run calculations to update plots only if not recording :)
                        val vector = classifier!!.calculateFeatureVector(sensorDataList)
                        val probabilities = classifier!!.classify(vector)
                        HomeFragment.pushNewClassificationResult(probabilities)
                        sensorDataList.clear()
                    }
                    RecordingFragment.STATE_TRAINING -> {
                        sensorDataList.clear() // just make sure it doesn't grow too much :)
                    }
                    RecordingFragment.STATE_RECORDING -> {
                        RecordingFragment.pushRecordingToModel()
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        sm.unregisterListener(this)
        wakeLock.release()
    }
}
