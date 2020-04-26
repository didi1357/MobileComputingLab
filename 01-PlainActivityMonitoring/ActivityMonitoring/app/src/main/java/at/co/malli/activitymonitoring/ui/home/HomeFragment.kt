package at.co.malli.activitymonitoring.ui.home

import android.graphics.Color
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProviders
import at.co.malli.activitymonitoring.MainActivity
import at.co.malli.activitymonitoring.R
import com.androidplot.xy.*
import java.text.NumberFormat
import java.util.*
import kotlin.collections.ArrayList


class HomeFragment : Fragment() {

    private lateinit var homeViewModel: HomeViewModel

    companion object {
        private val TAG: String? = HomeFragment::class.simpleName
        lateinit var graphSeriesFormat: LineAndPointFormatter

        val PLOT_X_LIMIT = 25

        lateinit var downstairsPlot: XYPlot
        lateinit var upstairsPlot: XYPlot
        lateinit var sittingPlot: XYPlot
        lateinit var standingPlot: XYPlot
        lateinit var walkingPlot: XYPlot
        lateinit var joggingPlot: XYPlot
        lateinit var plotArr: Array<XYPlot>

        val downstairsValues = mutableListOf<Float>()
        val upstairsValues = mutableListOf<Float>()
        val sittingValues = mutableListOf<Float>()
        val standingValues = mutableListOf<Float>()
        val walkingValues = mutableListOf<Float>()
        val joggingValues = mutableListOf<Float>()
        val timeSeriesData = arrayOf(
            downstairsValues, upstairsValues,
            sittingValues, standingValues, walkingValues, joggingValues
        )

        val timeAxis = ArrayList<Float>()

        fun pushNewClassificationResult(results: ArrayList<Float>) {
            for (i in results.indices)
                timeSeriesData[i].add(results[i])
            if (timeAxis.isEmpty())
                timeAxis.add(0.0f)
            else
                timeAxis.add(timeAxis.last() + MainActivity.DESIRED_WINDOW_MS / 1000.0f)

            updatePlot()
        }

        fun updatePlot() {
            val downstairsSeries = SimpleXYSeries(timeAxis, downstairsValues, "downstairs")
            val upstairsSeries = SimpleXYSeries(timeAxis, upstairsValues, "upstairs")
            val sittingSeries = SimpleXYSeries(timeAxis, sittingValues, "sitting")
            val standingSeries = SimpleXYSeries(timeAxis, standingValues, "standing")
            val walkingSeries = SimpleXYSeries(timeAxis, walkingValues, "walking")
            val joggingSeries = SimpleXYSeries(timeAxis, joggingValues, "jogging")
            for (plot in plotArr)
                plot.clear()
            downstairsPlot.addSeries(downstairsSeries, graphSeriesFormat)
            upstairsPlot.addSeries(upstairsSeries, graphSeriesFormat)
            sittingPlot.addSeries(sittingSeries, graphSeriesFormat)
            standingPlot.addSeries(standingSeries, graphSeriesFormat)
            walkingPlot.addSeries(walkingSeries, graphSeriesFormat)
            joggingPlot.addSeries(joggingSeries, graphSeriesFormat)
            var lowerLimit = 0.0f
            if (timeAxis.size > PLOT_X_LIMIT)
                lowerLimit = timeAxis[timeAxis.size - PLOT_X_LIMIT]
            for (plot in plotArr) {
                plot.legend.isVisible = false
                plot.setRangeBoundaries(-0.01, 1.01, BoundaryMode.FIXED)
                plot.setRangeStep(StepMode.SUBDIVIDE, 4.0)
                plot.setDomainBoundaries(lowerLimit, timeAxis.last(), BoundaryMode.FIXED)
                plot.graph.getLineLabelStyle(XYGraphWidget.Edge.LEFT).format = NumberFormat.getPercentInstance(
                    Locale.GERMAN)
                plot.redraw()
            }
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        homeViewModel =
            ViewModelProviders.of(this).get(HomeViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_home, container, false)
        downstairsPlot = root.findViewById(R.id.plotDownstairs) as XYPlot
        upstairsPlot = root.findViewById(R.id.plotUpstairs) as XYPlot
        sittingPlot = root.findViewById(R.id.plotSitting) as XYPlot
        standingPlot = root.findViewById(R.id.plotStanding) as XYPlot
        walkingPlot = root.findViewById(R.id.plotWalking) as XYPlot
        joggingPlot = root.findViewById(R.id.plotJogging) as XYPlot
        plotArr = arrayOf(
            downstairsPlot, upstairsPlot, sittingPlot,
            standingPlot, walkingPlot, joggingPlot
        )
        graphSeriesFormat = LineAndPointFormatter(Color.RED, Color.GREEN, Color.BLUE, null)
//        graphSeriesFormat.interpolationParams =
//            CatmullRomInterpolator.Params(10, CatmullRomInterpolator.Type.Centripetal)
        return root
    }
}
