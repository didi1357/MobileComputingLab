package at.co.malli.activitymonitoring.ui.recording

import android.app.Dialog
import android.content.DialogInterface
import android.hardware.Sensor
import android.hardware.SensorManager
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProviders
import at.co.malli.activitymonitoring.MainActivity.Companion.externalFilesDir
import at.co.malli.activitymonitoring.MainActivity.Companion.sensorDataList
import at.co.malli.activitymonitoring.R
import at.co.malli.activitymonitoring.SensorValue
import kotlinx.android.synthetic.main.fragment_recording.*
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.util.*


class RecordingFragment : Fragment(), View.OnClickListener {

    companion object {
        private val TAG: String? = RecordingFragment::class.simpleName

        const val STATE_STOPPED = 0
        const val STATE_RECORDING = 1
        var currentState: Int = STATE_STOPPED
    }

    private lateinit var recordingViewModel: RecordingViewModel
    private lateinit var recordButton: Button
    private lateinit var stopButton: Button



    override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        recordingViewModel =
                ViewModelProviders.of(this).get(RecordingViewModel::class.java)
        val rootView = inflater.inflate(R.layout.fragment_recording, container, false)
        recordButton = rootView.findViewById(R.id.recordButton) as Button
        stopButton = rootView.findViewById(R.id.stopButton) as Button
        recordButton.setOnClickListener(this)
        stopButton.setOnClickListener(this)

        applyState()

        return rootView
    }

    override fun onClick(v: View?) {
        when(v?.id) {
            R.id.recordButton -> recordPressed()
            R.id.stopButton -> stopPressed()
        }
    }

    fun applyState(new_state: Int?) {
        if (new_state != null)
            currentState = new_state

        if (currentState == STATE_RECORDING) {
            recordButton.isEnabled = false
            stopButton.isEnabled = true
        } else {
            recordButton.isEnabled = true
            stopButton.isEnabled = false
        }
    }

    fun recordPressed() {
        Log.v(TAG, "recordPressed")
        applyState(STATE_RECORDING)
    }

    fun stopPressed() {
        applyState(STATE_STOPPED)
        Log.v(TAG, "stopPressed")

        if (sensorDataList.isEmpty()) {
            Log.v(TAG, "List empty! Will not write anything!")
            return
        }

        val lastTimestamp = sensorDataList.last.timestamp
        val path = File(externalFilesDir, "$lastTimestamp.csv")
        val fOutStream = OutputStreamWriter(FileOutputStream(path))
        Log.v(TAG, "Opened file for writing: $path")
        for (data in sensorDataList) {
            val str = "${data.timestamp}, ${data.x}, ${data.y}, ${data.z}\n"
            fOutStream.write(str)
        }
        fOutStream.flush()
        fOutStream.close()
        Log.v(TAG, "sensorDataList had ${sensorDataList.size} entries.")

        sensorDataList.clear()
    }
}
