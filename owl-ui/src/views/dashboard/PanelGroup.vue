<template>
  <el-row :gutter="40" class="panel-group">
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handleSetLineChartData('newVisitis')">
        <div class="card-panel-icon-wrapper icon-people">
          <svg-icon icon-class="documentation" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            加密文件
          </div>
          <count-to :start-val="0" :end-val="fileStats.fileCount" :duration="2600" class="card-panel-num" />
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handleSetLineChartData('messages')">
        <div class="card-panel-icon-wrapper icon-message">
          <svg-icon icon-class="size" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            存储空间(MB)
          </div>
          <count-to :start-val="0" :end-val="storageMB" :duration="3000" class="card-panel-num" />
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handleSetLineChartData('purchases')">
        <div class="card-panel-icon-wrapper icon-money">
          <svg-icon icon-class="peoples" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            用户数
          </div>
          <count-to :start-val="0" :end-val="userCount" :duration="3200" class="card-panel-num" />
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handleSetLineChartData('shoppings')">
        <div class="card-panel-icon-wrapper icon-shopping">
          <svg-icon icon-class="upload" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            今日上传
          </div>
          <count-to :start-val="0" :end-val="todayUploads" :duration="3600" class="card-panel-num" />
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import CountTo from 'vue-count-to'
import { getFileStats } from '@/api/encry/file'
import { listUser } from '@/api/system/user'

export default {
  components: {
    CountTo
  },
  data() {
    return {
      fileStats: {
        fileCount: 0,
        storageUsed: 0
      },
      userCount: 0,
      todayUploads: 0
    }
  },
  computed: {
    storageMB() {
      return Math.round(this.fileStats.storageUsed / (1024 * 1024))
    }
  },
  mounted() {
    this.loadStats()
  },
  methods: {
    handleSetLineChartData(type) {
      this.$emit('handleSetLineChartData', type)
    },
    loadStats() {
      getFileStats().then(response => {
        const data = response.data && response.data.data ? response.data.data : response.data
        if (data) {
          this.fileStats = {
            fileCount: data.fileCount || 0,
            storageUsed: data.storageUsed || 0
          }
        }
      }).catch(() => {})
      
      this.loadUserCount()
    },
    loadUserCount() {
      listUser({ pageNum: 1, pageSize: 1 }).then(response => {
        if (response && response.total) {
          this.userCount = response.total
        }
      }).catch(() => {})
    }
  }
}
</script>

<style lang="scss" scoped>
// Grey Color Palette
$grey-50: #f2f2f3;
$grey-100: #e4e5e7;
$grey-200: #c9cacf;
$grey-300: #afb0b6;
$grey-400: #94959e;
$grey-500: #797b86;
$grey-600: #61626b;
$grey-700: #494a50;
$grey-800: #303136;
$grey-900: #18191b;
$grey-950: #111113;

.panel-group {
  margin-top: 18px;

  .card-panel-col {
    margin-bottom: 32px;
  }

  .card-panel {
    height: 108px;
    cursor: pointer;
    font-size: 12px;
    position: relative;
    overflow: hidden;
    color: $grey-700;
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba($grey-950, 0.04);
    border: 1px solid $grey-100;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba($grey-950, 0.08);

      .card-panel-icon-wrapper {
        color: #ffffff;
        background-color: $grey-800;
      }
    }

    .icon-people,
    .icon-message,
    .icon-money,
    .icon-shopping {
      color: $grey-600;
      background-color: $grey-100;
    }

    .card-panel-icon-wrapper {
      float: left;
      margin: 14px 0 0 14px;
      padding: 16px;
      transition: all 0.38s ease-out;
      border-radius: 10px;
    }

    .card-panel-icon {
      float: left;
      font-size: 48px;
    }

    .card-panel-description {
      float: right;
      font-weight: bold;
      margin: 26px;
      margin-left: 0px;

      .card-panel-text {
        line-height: 18px;
        color: $grey-500;
        font-size: 14px;
        margin-bottom: 12px;
        font-weight: 500;
      }

      .card-panel-num {
        font-size: 24px;
        color: $grey-900;
        font-weight: 600;
      }
    }
  }
}

@media (max-width:550px) {
  .card-panel-description {
    display: none;
  }

  .card-panel-icon-wrapper {
    float: none !important;
    width: 100%;
    height: 100%;
    margin: 0 !important;

    .svg-icon {
      display: block;
      margin: 14px auto !important;
      float: none !important;
    }
  }
}
</style>
