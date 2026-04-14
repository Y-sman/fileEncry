<template>
  <div class="upload-file">
    <el-upload
      multiple
      :action="uploadFileUrl"
      :data="data"
      :before-upload="handleBeforeUpload"
      :file-list="fileList"
      :limit="limit"
      :on-error="handleUploadError"
      :on-exceed="handleExceed"
      :on-success="handleUploadSuccess"
      :on-progress="handleUploadProgress"
      :show-file-list="false"
      :headers="headers"
      class="upload-file-uploader"
      ref="upload"
      :drag="drag"
    >
      <!-- 拖拽区域：支持拖拽或点击选择 -->
      <template v-if="drag">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击选择</em></div>
      </template>
      <!-- 仅点击按钮 -->
      <el-button v-else size="mini" type="primary">选取文件</el-button>
      <!-- 上传提示 -->
      <div class="el-upload__tip" slot="tip" v-if="showTip">
        请上传
        <template v-if="fileSize"> 大小不超过 <b style="color: #f56c6c">{{ fileSize }}MB</b> </template>
        <template v-if="fileType"> 格式为 <b style="color: #f56c6c">{{ fileType.join("/") }}</b> </template>
        的文件
      </div>
    </el-upload>

    <!-- 上传进度条 -->
    <div v-if="uploadProgress.show" class="upload-progress-container">
      <div class="upload-progress-info">
        <span class="upload-progress-filename">{{ uploadProgress.fileName }}</span>
        <span class="upload-progress-percent">{{ uploadProgress.percentage }}%</span>
      </div>
      <el-progress :percentage="uploadProgress.percentage" :status="uploadProgress.status" :stroke-width="8"></el-progress>
    </div>

    <!-- 文件列表 -->
    <transition-group class="upload-file-list el-upload-list el-upload-list--text" name="el-fade-in-linear" tag="ul">
      <li :key="file.url" class="el-upload-list__item ele-upload-list__item-content" v-for="(file, index) in fileList">
        <el-link :href="`${baseUrl}${file.url}`" :underline="false" target="_blank">
          <span class="el-icon-document"> {{ getFileName(file.name) }} </span>
        </el-link>
        <div class="ele-upload-list__item-content-action">
          <el-link :underline="false" @click="handleDelete(index)" type="danger">删除</el-link>
        </div>
      </li>
    </transition-group>
  </div>
</template>

<script>
import { getToken } from "@/utils/auth";

export default {
  name: "FileUpload",
  props: {
    // 值
    value: [String, Object, Array],
    // 自定义上传地址
    action: {
      type: String,
      default: '',
    },
    // 上传时附带的额外参数
    data: {
      type: Object,
      default: () => ({}),
    },
    // 数量限制
    limit: {
      type: Number,
      default: 5,
    },
    // 大小限制(MB)
    fileSize: {
      type: Number,
      default: 5,
    },
    // 文件类型, 例如['png', 'jpg', 'jpeg']
    fileType: {
      type: Array,
      default: () => ["doc", "xls", "ppt", "txt", "pdf"],
    },
    // 是否显示提示
    isShowTip: {
      type: Boolean,
      default: true
    },
    // 是否使用拖拽区域（拖拽或点击选择）
    drag: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      number: 0,
      uploadList: [],
      baseUrl: process.env.VUE_APP_BASE_API,
      headers: {
        Authorization: "Bearer " + getToken(),
      },
      fileList: [],
      // 上传进度
      uploadProgress: {
        show: false,
        percentage: 0,
        fileName: '',
        status: ''
      }
    };
  },
  watch: {
    value: {
      handler(val) {
        if (val) {
          let temp = 1;
          // 首先将值转为数组
          const list = Array.isArray(val) ? val : this.value.split(',');
          // 然后将数组转为对象数组
          this.fileList = list.map(item => {
            if (typeof item === "string") {
              item = { name: item, url: item };
            }
            item.uid = item.uid || new Date().getTime() + temp++;
            return item;
          });
        } else {
          this.fileList = [];
          return [];
        }
      },
      deep: true,
      immediate: true
    }
  },
  computed: {
    // 上传地址
    uploadFileUrl() {
      return this.action || process.env.VUE_APP_BASE_API + '/common/upload';
    },
    // 是否显示提示
    showTip() {
      return this.isShowTip && (this.fileType || this.fileSize);
    },
  },
  methods: {
    // 上传前校检格式和大小
    handleBeforeUpload(file) {
      // 校检文件类型（fileType 为空数组时不做类型限制）
      if (this.fileType && this.fileType.length > 0) {
        let fileExtension = "";
        if (file.name.lastIndexOf(".") > -1) {
          fileExtension = file.name.slice(file.name.lastIndexOf(".") + 1);
        }
        const isTypeOk = this.fileType.some((type) => {
          if (file.type.indexOf(type) > -1) return true;
          if (fileExtension && fileExtension.indexOf(type) > -1) return true;
          return false;
        });
        if (!isTypeOk) {
          this.$modal.msgError(`文件格式不正确, 请上传${this.fileType.join("/")}格式文件!`);
          return false;
        }
      }
      // 校检文件大小
      if (this.fileSize) {
        const isLt = file.size / 1024 / 1024 < this.fileSize;
        if (!isLt) {
          this.$modal.msgError(`上传文件大小不能超过 ${this.fileSize} MB!`);
          return false;
        }
      }
      // 初始化进度条
      this.uploadProgress = {
        show: true,
        percentage: 0,
        fileName: file.name,
        status: ''
      };
      this.number++;
      return true;
    },
    // 上传进度
    handleUploadProgress(event, file) {
      if (event.percent) {
        this.uploadProgress.percentage = Math.floor(event.percent);
      }
    },
    // 文件个数超出
    handleExceed() {
      this.$modal.msgError(`上传文件数量不能超过 ${this.limit} 个!`);
    },
    // 上传失败
    handleUploadError(err, file, fileList) {
      const msg = (err && err.message) || (err.response && err.response.data && err.response.data.msg) || "上传失败，请重试";
      this.$modal.msgError(msg);
      this.uploadProgress.status = 'exception';
      setTimeout(() => {
        this.resetUploadProgress();
      }, 1500);
      this.$emit("error", err);
    },
    // 上传成功回调（需检查响应是否为业务错误，如 code!==200 或非 JSON 成功结构）
    handleUploadSuccess(res) {
      const isError = !res || typeof res !== 'object' ||
        (res.code !== undefined && res.code !== 200);
      if (isError) {
        const msg = (res && typeof res === 'object' && (res.msg || res.message)) ||
          '上传失败，请确认已生成 RSA 密钥对';
        this.$modal.msgError(msg);
        this.uploadProgress.status = 'exception';
        setTimeout(() => {
          this.resetUploadProgress();
        }, 1500);
        this.$emit('error', { message: msg });
        return;
      }
      // 上传成功，进度条显示100%
      this.uploadProgress.percentage = 100;
      this.uploadProgress.status = 'success';
      setTimeout(() => {
        this.resetUploadProgress();
      }, 1000);
      this.$emit('success', res);
      const fileName = res.fileName || (res.data && res.data.originalName) || '';
      this.uploadList.push({ name: fileName, url: fileName });
      if (this.uploadList.length === this.number) {
        this.fileList = this.fileList.concat(this.uploadList);
        this.uploadList = [];
        this.number = 0;
        this.$emit("input", this.listToString(this.fileList));
      }
    },
    // 重置上传进度
    resetUploadProgress() {
      this.uploadProgress = {
        show: false,
        percentage: 0,
        fileName: '',
        status: ''
      };
    },
    // 删除文件
    handleDelete(index) {
      this.fileList.splice(index, 1);
      this.$emit("input", this.listToString(this.fileList));
    },
    // 获取文件名称
    getFileName(name) {
      if (name.lastIndexOf("/") > -1) {
        return name.slice(name.lastIndexOf("/") + 1);
      } else {
        return "";
      }
    },
    // 对象转成指定字符串分隔
    listToString(list, separator) {
      let strs = "";
      separator = separator || ",";
      for (let i in list) {
        strs += list[i].url + separator;
      }
      return strs != '' ? strs.substr(0, strs.length - 1) : '';
    }
  }
};
</script>

<style scoped lang="scss">
.upload-file-uploader {
  margin-bottom: 5px;
}

// 上传进度条样式
.upload-progress-container {
  margin: 12px 0;
  padding: 12px 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;

  .upload-progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .upload-progress-filename {
      font-size: 13px;
      color: #606266;
      max-width: 70%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .upload-progress-percent {
      font-size: 13px;
      color: #409eff;
      font-weight: 500;
    }
  }
}

.upload-file-list .el-upload-list__item {
  border: 1px solid #e4e7ed;
  line-height: 2;
  margin-bottom: 10px;
  position: relative;
}
.upload-file-list .ele-upload-list__item-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: inherit;
}
.ele-upload-list__item-content-action .el-link {
  margin-right: 10px;
}
</style>
