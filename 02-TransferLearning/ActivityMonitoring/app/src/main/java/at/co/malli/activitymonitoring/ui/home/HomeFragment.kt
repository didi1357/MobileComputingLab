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
        lateinit var graphSeriesFormatKNN: LineAndPointFormatter
        lateinit var graphSeriesFormatTL: LineAndPointFormatter
        lateinit var graphSeriesFormatBM: LineAndPointFormatter

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
        val downstairsValuesTL = mutableListOf<Float>()
        val upstairsValuesTL = mutableListOf<Float>()
        val sittingValuesTL = mutableListOf<Float>()
        val standingValuesTL = mutableListOf<Float>()
        val walkingValuesTL = mutableListOf<Float>()
        val joggingValuesTL = mutableListOf<Float>()
        val downstairsValuesBM = mutableListOf<Float>()
        val upstairsValuesBM = mutableListOf<Float>()
        val sittingValuesBM = mutableListOf<Float>()
        val standingValuesBM = mutableListOf<Float>()
        val walkingValuesBM = mutableListOf<Float>()
        val joggingValuesBM = mutableListOf<Float>()
        val timeSeriesDataKNN = arrayOf(
            downstairsValuesKNN, upstairsValuesKNN,
            sittingValuesKNN, standingValuesKNN, walkingValuesKNN, joggingValuesKNN
        )
        val timeSeriesDataTL = arrayOf(
            downstairsValuesTL, upstairsValuesTL,
            sittingValuesTL, standingValuesTL, walkingValuesTL, joggingValuesTL
        )
        val timeSeriesDataBM = arrayOf(
            downstairsValuesBM, upstairsValuesBM,
            sittingValuesBM, standingValuesBM, walkingValuesBM, joggingValuesBM
        )

        val timeAxis = ArrayList<Float>()

        fun pushNewClassificationResult(
            resultsKNN: ArrayList<Float>,
            resultsTL: FloatArray,
            resultsBM: FloatArray
        ) {
            for (i in resultsKNN.indices) {
                timeSeriesDataKNN[i].add(resultsKNN[i])
                timeSeriesDataTL[i].add(resultsTL[i])
                timeSeriesDataBM[i].add(resultsBM[i])
            }
            if (timeAxis.isEmpty())
                timeAxis.add(0.0f)
            else {
                var next = timeAxis.last()
                next += MainActivity.WINDOW_N * MainActivity.APPROX_SENS_VAL_DELAY_MS / 1000.0f
                timeAxis.add(next)
            }

            updatePlot()
        }

        fun updatePlot() {
            val downstairsSeriesKNN = SimpleXYSeries(timeAxis, downstairsValuesKNN, "downstairs")
            val upstairsSeriesKNN = SimpleXYSeries(timeAxis, upstairsValuesKNN, "upstairs")
            val sittingSeriesKNN = SimpleXYSeries(timeAxis, sittingValuesKNN, "sitting")
            val standingSeriesKNN = SimpleXYSeries(timeAxis, standingValuesKNN, "standing")
            val walkingSeriesKNN = SimpleXYSeries(timeAxis, walkingValuesKNN, "walking")
            val joggingSeriesKNN = SimpleXYSeries(timeAxis, joggingValuesKNN, "jogging")
            val downstairsSeriesTF = SimpleXYSeries(timeAxis, downstairsValuesTL, "downstairs")
            val upstairsSeriesTF = SimpleXYSeries(timeAxis, upstairsValuesTL, "upstairs")
            val sittingSeriesTF = SimpleXYSeries(timeAxis, sittingValuesTL, "sitting")
            val standingSeriesTF = SimpleXYSeries(timeAxis, standingValuesTL, "standing")
            val walkingSeriesTF = SimpleXYSeries(timeAxis, walkingValuesTL, "walking")
            val joggingSeriesTF = SimpleXYSeries(timeAxis, joggingValuesTL, "jogging")
            val downstairsSeriesBM = SimpleXYSeries(timeAxis, downstairsValuesBM, "downstairs")
            val upstairsSeriesBM = SimpleXYSeries(timeAxis, upstairsValuesBM, "upstairs")
            val sittingSeriesBM = SimpleXYSeries(timeAxis, sittingValuesBM, "sitting")
            val standingSeriesBM = SimpleXYSeries(timeAxis, standingValuesBM, "standing")
            val walkingSeriesBM = SimpleXYSeries(timeAxis, walkingValuesBM, "walking")
            val joggingSeriesBM = SimpleXYSeries(timeAxis, joggingValuesBM, "jogging")
            for (plot in plotArr)
                plot.clear()
            downstairsPlot.addSeries(downstairsSeriesKNN, graphSeriesFormatKNN)
            upstairsPlot.addSeries(upstairsSeriesKNN, graphSeriesFormatKNN)
            sittingPlot.addSeries(sittingSeriesKNN, graphSeriesFormatKNN)
            standingPlot.addSeries(standingSeriesKNN, graphSeriesFormatKNN)
            walkingPlot.addSeries(walkingSeriesKNN, graphSeriesFormatKNN)
            joggingPlot.addSeries(joggingSeriesKNN, graphSeriesFormatKNN)
            downstairsPlot.addSeries(downstairsSeriesTF, graphSeriesFormatTL)
            upstairsPlot.addSeries(upstairsSeriesTF, graphSeriesFormatTL)
            sittingPlot.addSeries(sittingSeriesTF, graphSeriesFormatTL)
            standingPlot.addSeries(standingSeriesTF, graphSeriesFormatTL)
            walkingPlot.addSeries(walkingSeriesTF, graphSeriesFormatTL)
            joggingPlot.addSeries(joggingSeriesTF, graphSeriesFormatTL)
            downstairsPlot.addSeries(downstairsSeriesBM, graphSeriesFormatBM)
            upstairsPlot.addSeries(upstairsSeriesBM, graphSeriesFormatBM)
            sittingPlot.addSeries(sittingSeriesBM, graphSeriesFormatBM)
            standingPlot.addSeries(standingSeriesBM, graphSeriesFormatBM)
            walkingPlot.addSeries(walkingSeriesBM, graphSeriesFormatBM)
            joggingPlot.addSeries(joggingSeriesBM, graphSeriesFormatBM)
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
        graphSeriesFormatTL = LineAndPointFormatter(Color.BLUE, Color.BLUE, Color.TRANSPARENT, null)
        graphSeriesFormatBM = LineAndPointFormatter(
            Color.GREEN, Color.GREEN, Color.TRANSPARENT, null
        )
        return root
    }
}
