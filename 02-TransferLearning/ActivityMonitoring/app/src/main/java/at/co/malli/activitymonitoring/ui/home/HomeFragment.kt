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
        lateinit var graphSeriesFormatTF: LineAndPointFormatter
        lateinit var graphSeriesFormatKNN: LineAndPointFormatter

        val PLOT_X_LIMIT = 25

        lateinit var downstairsPlot: XYPlot
        lateinit var upstairsPlot: XYPlot
        lateinit var sittingPlot: XYPlot
        lateinit var standingPlot: XYPlot
        lateinit var walkingPlot: XYPlot
        lateinit var joggingPlot: XYPlot
        lateinit var plotArr: Array<XYPlot>

        val downstairsValuesKNN = mutableListOf<Float>()
        val upstairsValuesKNN = mutableListOf<Float>()
        val sittingValuesKNN = mutableListOf<Float>()
        val standingValuesKNN = mutableListOf<Float>()
        val walkingValuesKNN = mutableListOf<Float>()
        val joggingValuesKNN = mutableListOf<Float>()
        val downstairsValuesTF = mutableListOf<Float>()
        val upstairsValuesTF = mutableListOf<Float>()
        val sittingValuesTF = mutableListOf<Float>()
        val standingValuesTF = mutableListOf<Float>()
        val walkingValuesTF = mutableListOf<Float>()
        val joggingValuesTF = mutableListOf<Float>()
        val timeSeriesDataTF = arrayOf(
            downstairsValuesTF, upstairsValuesTF,
            sittingValuesTF, standingValuesTF, walkingValuesTF, joggingValuesTF
        )
        val timeSeriesDataKNN = arrayOf(
            downstairsValuesKNN, upstairsValuesKNN,
            sittingValuesKNN, standingValuesKNN, walkingValuesKNN, joggingValuesKNN
        )

        val timeAxis = ArrayList<Float>()

        fun pushNewClassificationResult(resultsKNN: ArrayList<Float>, resultsTF: ArrayList<Float>) {
            for (i in resultsKNN.indices) {
                timeSeriesDataKNN[i].add(resultsKNN[i])
                timeSeriesDataTF[i].add(resultsTF[i])
            }
            if (timeAxis.isEmpty())
                timeAxis.add(0.0f)
            else
                timeAxis.add(timeAxis.last() + MainActivity.DESIRED_WINDOW_MS / 1000.0f)

            updatePlot()
        }

        fun updatePlot() {
            val downstairsSeriesKNN = SimpleXYSeries(timeAxis, downstairsValuesKNN, "downstairs")
            val upstairsSeriesKNN = SimpleXYSeries(timeAxis, upstairsValuesKNN, "upstairs")
            val sittingSeriesKNN = SimpleXYSeries(timeAxis, sittingValuesKNN, "sitting")
            val standingSeriesKNN = SimpleXYSeries(timeAxis, standingValuesKNN, "standing")
            val walkingSeriesKNN = SimpleXYSeries(timeAxis, walkingValuesKNN, "walking")
            val joggingSeriesKNN = SimpleXYSeries(timeAxis, joggingValuesKNN, "jogging")
            val downstairsSeriesTF = SimpleXYSeries(timeAxis, downstairsValuesKNN, "downstairs")
            val upstairsSeriesTF = SimpleXYSeries(timeAxis, upstairsValuesKNN, "upstairs")
            val sittingSeriesTF = SimpleXYSeries(timeAxis, sittingValuesKNN, "sitting")
            val standingSeriesTF = SimpleXYSeries(timeAxis, standingValuesKNN, "standing")
            val walkingSeriesTF = SimpleXYSeries(timeAxis, walkingValuesKNN, "walking")
            val joggingSeriesTF = SimpleXYSeries(timeAxis, joggingValuesKNN, "jogging")
            for (plot in plotArr)
                plot.clear()
            downstairsPlot.addSeries(downstairsSeriesKNN, graphSeriesFormatKNN)
            upstairsPlot.addSeries(upstairsSeriesKNN, graphSeriesFormatKNN)
            sittingPlot.addSeries(sittingSeriesKNN, graphSeriesFormatKNN)
            standingPlot.addSeries(standingSeriesKNN, graphSeriesFormatKNN)
            walkingPlot.addSeries(walkingSeriesKNN, graphSeriesFormatKNN)
            joggingPlot.addSeries(joggingSeriesKNN, graphSeriesFormatKNN)
            downstairsPlot.addSeries(downstairsSeriesTF, graphSeriesFormatTF)
            upstairsPlot.addSeries(upstairsSeriesTF, graphSeriesFormatTF)
            sittingPlot.addSeries(sittingSeriesTF, graphSeriesFormatTF)
            standingPlot.addSeries(standingSeriesTF, graphSeriesFormatTF)
            walkingPlot.addSeries(walkingSeriesTF, graphSeriesFormatTF)
            joggingPlot.addSeries(joggingSeriesTF, graphSeriesFormatTF)
            var lowerLimit = 0.0f
            if (timeAxis.size > PLOT_X_LIMIT)
                lowerLimit = timeAxis[timeAxis.size - PLOT_X_LIMIT]
            for (plot in plotArr) {
                plot.legend.isVisible = false
                plot.setRangeBoundaries(-0.01, 1.01, BoundaryMode.FIXED)
                plot.setRangeStep(StepMode.SUBDIVIDE, 4.0)
                plot.setDomainBoundaries(lowerLimit, timeAxis.last(), BoundaryMode.FIXED)
                plot.graph.getLineLabelStyle(XYGraphWidget.Edge.LEFT).format =
                    NumberFormat.getPercentInstance(
                        Locale.GERMAN
                    )
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
        graphSeriesFormatKNN = LineAndPointFormatter(Color.RED, Color.RED, Color.TRANSPARENT, null)
        graphSeriesFormatTF = LineAndPointFormatter(Color.BLUE, Color.BLUE, Color.TRANSPARENT, null)
//        graphSeriesFormat.interpolationParams =
//            CatmullRomInterpolator.Params(10, CatmullRomInterpolator.Type.Centripetal)
        return root
    }
}
