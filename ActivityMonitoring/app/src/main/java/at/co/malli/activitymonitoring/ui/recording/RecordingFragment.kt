package at.co.malli.activitymonitoring.ui.recording

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import at.co.malli.activitymonitoring.R

class RecordingFragment : Fragment() {

    private lateinit var recordingViewModel: RecordingViewModel

    override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        recordingViewModel =
                ViewModelProviders.of(this).get(RecordingViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_recording, container, false)
        val textView: TextView = root.findViewById(R.id.text_gallery)
        recordingViewModel.text.observe(viewLifecycleOwner, Observer {
            textView.text = it
        })
        return root
    }
}
