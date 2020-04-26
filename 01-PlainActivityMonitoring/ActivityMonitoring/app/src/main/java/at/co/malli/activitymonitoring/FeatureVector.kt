package at.co.malli.activitymonitoring

data class FeatureVector(val values: ArrayList<Double>, val classNr: Int) {
    companion object {
        val CLASSNR_UNDEFINED = Int.MAX_VALUE
    }
}