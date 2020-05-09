package at.co.malli.activitymonitoring.ui.recording

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.RadioGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProviders
import at.co.malli.activitymonitoring.MainActivity
import at.co.malli.activitymonitoring.MainActivity.Companion.externalFilesDir
import at.co.malli.activitymonitoring.MainActivity.Companion.sensorDataList
import at.co.malli.activitymonitoring.R
import at.co.malli.activitymonitoring.TransferLearningModelWrapper
import java.io.File


class RecordingFragment : Fragment(), View.OnClickListener, RadioGroup.OnCheckedChangeListener {

    companion object {
        fun updateSegmentCounts(currentModel: TransferLearningModelWrapper) {
            downstairsTV.text = "${currentModel.getSegmentCount(ACTIVITY_DOWNSTAIRS)}"
            joggingTV.text = "${currentModel.getSegmentCount(ACTIVITY_JOGGING)}"
            sittingTV.text = "${currentModel.getSegmentCount(ACTIVITY_SITTING)}"
            standingTV.text = "${currentModel.getSegmentCount(ACTIVITY_STANDING)}"
            upstairsTV.text = "${currentModel.getSegmentCount(ACTIVITY_UPSTAIRS)}"
            walkingTV.text = "${currentModel.getSegmentCount(ACTIVITY_WALKING)}"
        }

        private val TAG: String? = RecordingFragment::class.simpleName

        const val ACTIVITY_INVALID = -1
        const val ACTIVITY_DOWNSTAIRS = 0
        const val ACTIVITY_JOGGING = 1
        const val ACTIVITY_SITTING = 2
        const val ACTIVITY_STANDING = 3
        const val ACTIVITY_UPSTAIRS = 4
        const val ACTIVITY_WALKING = 5
        var currentRecordingActivity = ACTIVITY_INVALID

        const val STATE_STOPPED = 0
        const val STATE_RECORDING = 1
        const val STATE_TRAINING = 2
        var currentState: Int = STATE_STOPPED

        const val POSITION_HAND = 0
        const val POSITION_POCKET = 1
        var currentPositionSelection: Int = POSITION_HAND
        lateinit var downstairsBut: Button
        lateinit var joggingBut: Button
        lateinit var sittingBut: Button
        lateinit var standingBut: Button
        lateinit var upstairsBut: Button
        lateinit var walkingBut: Button
        lateinit var trainingBut: Button
        lateinit var positionRG: RadioGroup
        lateinit var stopBut: Button
        lateinit var loadBut: Button
        lateinit var saveBut: Button
        lateinit var downstairsTV: TextView
        lateinit var joggingTV: TextView
        lateinit var sittingTV: TextView
        lateinit var standingTV: TextView
        lateinit var upstairsTV: TextView
        lateinit var walkingTV: TextView
        lateinit var lossTV: TextView
    }

    private lateinit var recordingViewModel: RecordingViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        recordingViewModel =
            ViewModelProviders.of(this).get(RecordingViewModel::class.java)
        val rootView = inflater.inflate(R.layout.fragment_recording, container, false)
        downstairsBut = rootView.findViewById(R.id.recordDownstairsButton) as Button
        joggingBut = rootView.findViewById(R.id.recordJoggingButton) as Button
        sittingBut = rootView.findViewById(R.id.recordSittingButton) as Button
        standingBut = rootView.findViewById(R.id.recordStandingButton) as Button
        upstairsBut = rootView.findViewById(R.id.recordUpstairsButton) as Button
        walkingBut = rootView.findViewById(R.id.recordWalkingButton) as Button
        trainingBut = rootView.findViewById(R.id.doTrainingButton) as Button
        positionRG = rootView.findViewById(R.id.positionRadioGroup) as RadioGroup
        stopBut = rootView.findViewById(R.id.stopButton) as Button
        loadBut = rootView.findViewById(R.id.loadButton) as Button
        saveBut = rootView.findViewById(R.id.saveButton) as Button
        downstairsTV = rootView.findViewById(R.id.downstairsTextView) as TextView
        joggingTV = rootView.findViewById(R.id.joggingTextView) as TextView
        sittingTV = rootView.findViewById(R.id.sittingTextView) as TextView
        standingTV = rootView.findViewById(R.id.standingTextView) as TextView
        upstairsTV = rootView.findViewById(R.id.upstairsTextView) as TextView
        walkingTV = rootView.findViewById(R.id.walkingTextView) as TextView
        lossTV = rootView.findViewById(R.id.lossTextView) as TextView
        downstairsBut.setOnClickListener(this)
        joggingBut.setOnClickListener(this)
        sittingBut.setOnClickListener(this)
        standingBut.setOnClickListener(this)
        upstairsBut.setOnClickListener(this)
        walkingBut.setOnClickListener(this)
        trainingBut.setOnClickListener(this)
        stopBut.setOnClickListener(this)
        loadBut.setOnClickListener(this)
        saveBut.setOnClickListener(this)

        positionRG.setOnCheckedChangeListener(this)

        applyStateUI(null)

        return rootView
    }

    override fun onClick(v: View?) {
        when (v?.id) {
            R.id.recordDownstairsButton -> recordPressed(ACTIVITY_DOWNSTAIRS)
            R.id.recordJoggingButton -> recordPressed(ACTIVITY_JOGGING)
            R.id.recordSittingButton -> recordPressed(ACTIVITY_SITTING)
            R.id.recordStandingButton -> recordPressed(ACTIVITY_STANDING)
            R.id.recordUpstairsButton -> recordPressed(ACTIVITY_UPSTAIRS)
            R.id.recordWalkingButton -> recordPressed(ACTIVITY_WALKING)
            R.id.doTrainingButton -> doTraining()
            R.id.loadButton -> loadPressed()
            R.id.saveButton -> savePressed()
            R.id.stopButton -> stopPressed()
        }
    }

    private fun loadPressed() {
        Log.v(TAG, "loadPressed")
        val learnedFilePath = File(externalFilesDir, "$currentPositionSelection.learned")
        MainActivity.tlModels[currentPositionSelection].loadModel(learnedFilePath)
    }

    private fun savePressed() {
        Log.v(TAG, "savePressed")
        val learnedFilePath = File(externalFilesDir, "$currentPositionSelection.learned")
        MainActivity.tlModels[currentPositionSelection].saveModel(learnedFilePath)
    }

    fun applyStateUI(new_state: Int?) {
        if (new_state != null)
            currentState = new_state

        when (currentState) {
            STATE_STOPPED -> {
                downstairsBut.isEnabled = true
                joggingBut.isEnabled = true
                sittingBut.isEnabled = true
                standingBut.isEnabled = true
                upstairsBut.isEnabled = true
                walkingBut.isEnabled = true
                trainingBut.isEnabled = true
                positionRG.isEnabled = true
                stopBut.isEnabled = false
            }
            STATE_RECORDING -> {
                downstairsBut.isEnabled = false
                joggingBut.isEnabled = false
                sittingBut.isEnabled = false
                standingBut.isEnabled = false
                upstairsBut.isEnabled = false
                walkingBut.isEnabled = false
                trainingBut.isEnabled = false
                positionRG.isEnabled = false
                stopBut.isEnabled = true
            }
            STATE_TRAINING -> {
                downstairsBut.isEnabled = false
                joggingBut.isEnabled = false
                sittingBut.isEnabled = false
                standingBut.isEnabled = false
                upstairsBut.isEnabled = false
                walkingBut.isEnabled = false
                trainingBut.isEnabled = false
                positionRG.isEnabled = false
                stopBut.isEnabled = true
            }
        }
    }

    fun recordPressed(activity_id: Int) {
        Log.v(TAG, "recordPressed: $activity_id")
        currentRecordingActivity = activity_id
        applyStateUI(STATE_RECORDING)
        sensorDataList.clear() //TODO: locking on sensorDataList?
    }

    fun doTraining() {
        Log.v(TAG, "doTrainingPressed")
        applyStateUI(STATE_TRAINING)
    }

    fun stopPressed() {
        Log.v(TAG, "stopPressed")
        if(currentState == STATE_TRAINING)
            MainActivity.tlModels[currentPositionSelection].disableTraining()
        applyStateUI(STATE_STOPPED)
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
