<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // echarts theme
import resize from './mixins/resize'

const animationDuration = 6000

export default {
  mixins: [resize],
  props: {
    className: {
      type: String,
      default: 'chart'
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '300px'
    }
  },
  data() {
    return {
      chart: null
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  },
  beforeDestroy() {
    if (!this.chart) {
      return
    }
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')

      this.chart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          top: 10,
          left: '2%',
          right: '2%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [{
          type: 'category',
          data: ['<1MB', '1-10MB', '10-50MB', '50-100MB', '100-500MB', '>500MB'],
          axisTick: {
            alignWithLabel: true
          }
        }],
        yAxis: [{
          type: 'value',
          name: '文件数量',
          axisTick: {
            show: false
          }
        }],
        series: [{
          name: 'AES加密',
          type: 'bar',
          stack: 'files',
          barWidth: '60%',
          data: [79, 52, 200, 334, 390, 330],
          animationDuration
        }, {
          name: 'DES加密',
          type: 'bar',
          stack: 'files',
          barWidth: '60%',
          data: [80, 52, 200, 334, 390, 330],
          animationDuration
        }]
      })
    }
  }
}
</script>
