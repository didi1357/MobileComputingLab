package at.co.malli.activitymonitoring.ui.recording

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
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter


class RecordingFragment : Fragment(), View.OnClickListener {

    companion object {
        private val TAG: String? = RecordingFragment::class.simpleName

        const val STATE_NOT_RECORDING = 0
        const val STATE_RECORDING = 1
        var currentState: Int = STATE_NOT_RECORDING
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

        applyState(null)

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
        sensorDataList.clear() //TODO: locking on sensorDataList
    }

    fun stopPressed() {
        applyState(STATE_NOT_RECORDING)
        Log.v(TAG, "stopPressed")

        if (sensorDataList.isEmpty()) {
            Log.v(TAG, "List empty! Will not write anything!")
            return
        }

        val lastTimestamp = sensorDataList[sensorDataList.lastIndex].timestamp
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
    }
}
