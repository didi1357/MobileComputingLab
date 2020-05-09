package at.co.malli.activitymonitoring.ui.recording

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.RadioGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProviders
import at.co.malli.activitymonitoring.MainActivity.Companion.externalFilesDir
import at.co.malli.activitymonitoring.MainActivity.Companion.sensorDataList
import at.co.malli.activitymonitoring.R
import kotlinx.android.synthetic.main.fragment_recording.*
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter


class RecordingFragment : Fragment(), View.OnClickListener, RadioGroup.OnCheckedChangeListener {

    private fun toFloatArray(list: List<Float>): FloatArray? {
        var i = 0
        val array = FloatArray(list.size)
        for (f in list) {
            array[i++] = f ?: Float.NaN
        }
        return array
    }

    companion object {
        private val TAG: String? = RecordingFragment::class.simpleName

        const val STATE_STOPPED = 0
        const val STATE_RECORDING = 1
        const val STATE_TRAINING = 1
        var currentState: Int = STATE_STOPPED

        const val POSITION_HAND = 0
        const val POSITION_POCKET = 1
        var currentPositionSelection: Int = POSITION_HAND
    }

    private lateinit var recordingViewModel: RecordingViewModel
    private lateinit var recordDownstairsButton: Button
    private lateinit var recordJoggingButton: Button
    private lateinit var recordSittingButton: Button
    private lateinit var recordStandingButton: Button
    private lateinit var recordUpstairsButton: Button
    private lateinit var recordWalkingButton: Button
    private lateinit var doTrainingButton: Button
    private lateinit var stopButton: Button

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        recordingViewModel =
            ViewModelProviders.of(this).get(RecordingViewModel::class.java)
        val rootView = inflater.inflate(R.layout.fragment_recording, container, false)
        recordDownstairsButton = rootView.findViewById(R.id.recordDownstairsButton) as Button
        recordJoggingButton = rootView.findViewById(R.id.recordJoggingButton) as Button
        recordSittingButton = rootView.findViewById(R.id.recordSittingButton) as Button
        recordStandingButton = rootView.findViewById(R.id.recordStandingButton) as Button
        recordUpstairsButton = rootView.findViewById(R.id.recordUpstairsButton) as Button
        recordWalkingButton = rootView.findViewById(R.id.recordWalkingButton) as Button
        doTrainingButton = rootView.findViewById(R.id.doTrainingButton) as Button
        stopButton = rootView.findViewById(R.id.stopButton) as Button
        recordDownstairsButton.setOnClickListener(this)
        recordJoggingButton.setOnClickListener(this)
        recordSittingButton.setOnClickListener(this)
        recordStandingButton.setOnClickListener(this)
        recordUpstairsButton.setOnClickListener(this)
        recordWalkingButton.setOnClickListener(this)
        doTrainingButton.setOnClickListener(this)
        stopButton.setOnClickListener(this)

        positionRadioGroup.setOnCheckedChangeListener(this)

        applyState(null)

        return rootView
    }

    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.recordDownstairsButton -> recordPressed(0)
            R.id.recordJoggingButton -> recordPressed(1)
            R.id.recordSittingButton -> recordPressed(2)
            R.id.recordStandingButton -> recordPressed(3)
            R.id.recordUpstairsButton -> recordPressed(4)
            R.id.recordWalkingButton -> recordPressed(5)
            R.id.doTrainingButton -> doTraining()
            R.id.loadButton -> loadPressed()
            R.id.saveButton -> savePressed()
            R.id.stopButton -> stopPressed()
        }
    }

    private fun loadPressed() {
        Log.v(TAG, "loadPressed")
    }

    private fun savePressed() {
        Log.v(TAG, "savePressed")
    }

    fun applyState(new_state: Int?) {
        if (new_state != null)
            currentState = new_state

        when (currentState) {
            STATE_STOPPED -> {
                recordDownstairsButton.isEnabled = true
                stopButton.isEnabled = false
            }
            STATE_RECORDING -> {
                recordDownstairsButton.isEnabled = false
                stopButton.isEnabled = true
            }
            STATE_TRAINING -> {

            }
        }
    }

    fun recordPressed(activity_id: Int) {
        Log.v(TAG, "recordPressed: $activity_id")
        applyState(STATE_RECORDING)
        sensorDataList.clear() //TODO: locking on sensorDataList?
    }

    fun doTraining() {
        Log.v(TAG, "doTrainingPressed")
        applyState(STATE_TRAINING)
    }

    fun stopPressed() {
        applyState(STATE_STOPPED)
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

    override fun onCheckedChanged(group: RadioGroup?, checkedId: Int) {
        if (group?.id == R.id.positionRadioGroup) {
            if (checkedId == R.id.handRadioButton)
                currentPositionSelection = POSITION_HAND
            else if (checkedId == R.id.pocketRadioButton)
                currentPositionSelection = POSITION_POCKET
        }
    }
}
