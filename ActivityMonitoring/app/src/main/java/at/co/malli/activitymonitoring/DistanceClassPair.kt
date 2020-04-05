package at.co.malli.activitymonitoring

import java.lang.Integer.max
import java.lang.Integer.min

data class DistanceClassPair(val distance: Double, val classNr: Int) :
    Comparable<DistanceClassPair> {
    override fun compareTo(other: DistanceClassPair): Int {
        val difference = this.distance - other.distance
        return if (difference > 0)
            max(1, difference.toInt())
        else
            min(-1, difference.toInt())
    }


}

