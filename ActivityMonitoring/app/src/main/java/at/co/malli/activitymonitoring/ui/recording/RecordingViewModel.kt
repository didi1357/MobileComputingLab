package at.co.malli.activitymonitoring.ui.recording

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class RecordingViewModel : ViewModel() {

    private val _text = MutableLiveData<String>().apply {
        value = "This is recording Fragment"
    }
    val text: LiveData<String> = _text
}