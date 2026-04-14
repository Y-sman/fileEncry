<template>
  <div class="app-container">
    <el-form :model="queryParams" ref="queryForm" size="small" :inline="true" v-show="showSearch" label-width="90px">
      <el-form-item label="文件名" prop="originalName">
        <el-input
          v-model="queryParams.originalName"
          placeholder="请输入文件名"
          clearable
          @keyup.enter.native="handleQuery"
        />
      </el-form-item>
      <el-form-item label="加密算法" prop="encryptAlgo">
        <el-select v-model="queryParams.encryptAlgo" placeholder="请选择" clearable>
          <el-option label="AES" value="AES" />
          <el-option label="DES" value="DES" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" icon="el-icon-search" size="mini" @click="handleQuery">搜索</el-button>
        <el-button icon="el-icon-refresh" size="mini" @click="resetQuery">重置</el-button>
      </el-form-item>
    </el-form>

    <el-row :gutter="10" class="mb8">
      <el-col :span="1.5">
        <el-button
          type="primary"
          plain
          icon="el-icon-upload2"
          size="mini"
          @click="handleUpload"
          v-hasPermi="['encry:file:upload']"
        >加密上传</el-button>
      </el-col>
      <el-col :span="1.5">
        <el-button
          type="danger"
          plain
          icon="el-icon-delete"
          size="mini"
          :disabled="multiple"
          @click="handleDelete"
          v-hasPermi="['encry:file:remove']"
        >删除</el-button>
      </el-col>
      <right-toolbar :showSearch.sync="showSearch" @queryTable="getList"></right-toolbar>
    </el-row>

    <el-table v-loading="loading" :data="fileList" :row-key="getRowKey" @selection-change="handleSelectionChange">
      <template slot="empty">
        <el-empty description="暂无数据"></el-empty>
      </template>
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column label="文件名" align="center" prop="originalName" :show-overflow-tooltip="true">
        <template slot-scope="scope">{{ scope.row.originalName || scope.row.original_name }}</template>
      </el-table-column>
      <el-table-column label="加密算法" align="center">
        <template slot-scope="scope">{{ scope.row.encryptAlgo || scope.row.encrypt_algo }}</template>
      </el-table-column>
      <el-table-column label="文件大小" align="center">
        <template slot-scope="scope">{{ formatSize(scope.row.fileSize != null ? scope.row.fileSize : scope.row.file_size) }}</template>
      </el-table-column>
      <el-table-column label="上传时间" align="center">
        <template slot-scope="scope">{{ parseTime(scope.row.createTime || scope.row.create_time) }}</template>
      </el-table-column>
      <el-table-column label="哈希值" align="center" min-width="200" :show-overflow-tooltip="true">
        <template slot-scope="scope">{{ scope.row.fileHash || scope.row.file_hash || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" align="center" class-name="small-padding fixed-width" width="210">
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="text"
            icon="el-icon-download"
            @click="handleDownload(scope.row)"
            v-hasPermi="['encry:file:download']"
          >解密下载</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-document"
            @click="handleGetHash(scope.row)"
            v-hasPermi="['encry:file:query']"
          >获取哈希</el-button>
          <el-button
            size="mini"
            type="text"
            icon="el-icon-delete"
            @click="handleDelete(scope.row)"
            v-hasPermi="['encry:file:remove']"
            style="color: #E47470;"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination
      v-show="total>0"
      :total="total"
      :page.sync="queryParams.pageNum"
      :limit.sync="queryParams.pageSize"
      @pagination="getList"
    />

    <!-- 加密上传对话框 -->
    <el-dialog :title="upload.title" :visible.sync="upload.open" width="500px" append-to-body>
      <el-form :model="upload" label-width="110px" label-position="left">
        <el-alert
          title="混合加密：文件用 AES/DES 对称加密，密钥用 RSA 非对称加密保护"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px;"
        />
        <el-form-item label="对称加密算法">
          <el-radio-group v-model="upload.encryptAlgo">
            <el-radio label="AES">AES</el-radio>
            <el-radio label="DES">DES</el-radio>
          </el-radio-group>
          <div style="font-size: 12px; color: #909399; margin-top: 4px;">（对称密钥由您的 RSA 公钥加密存储）</div>
        </el-form-item>
        <el-form-item v-if="upload.encryptAlgo === 'AES'" label="AES 模式">
          <el-select v-model="upload.aesMode" placeholder="请选择" style="width: 120px;">
            <el-option label="CBC" value="CBC" />
            <el-option label="GCM" value="GCM" />
            <el-option label="ECB" value="ECB" />
          </el-select>
        </el-form-item>
        <el-form-item label="对称密钥">
          <el-input
            v-model="upload.userKey"
            type="textarea"
            :rows="2"
            placeholder="留空则自动生成随机密钥；可输入十六进制或字符串"
          />
          <el-button size="small" type="primary" plain style="margin-top: 6px;" @click="generateRandomKey">生成随机密钥</el-button>
        </el-form-item>
        <el-form-item label="选择文件">
          <FileUpload
            :key="upload.key"
            :limit="1"
            :file-type="[]"
            :file-size="50"
            :action="uploadAction"
            :data="uploadFormData"
            :is-show-tip="true"
            :drag="true"
            @success="handleUploadSuccess"
            @error="handleUploadError"
          />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="upload.open = false">关 闭</el-button>
      </div>
    </el-dialog>

    <!-- 上传成功-哈希值对话框 -->
    <el-dialog title="文件哈希值（请妥善保管，用于下载时完整性校验）" :visible.sync="hashDialog.open" width="600px" append-to-body>
      <el-alert title="SHA256 哈希值可用于下载时校验文件是否被篡改" type="info" :closable="false" show-icon style="margin-bottom: 15px;" />
      <el-input type="textarea" :value="hashDialog.content" :rows="4" readonly />
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="copyHash">复 制</el-button>
        <el-button type="success" @click="exportHashFile">导出哈希文件</el-button>
        <el-button @click="hashDialog.open = false">关 闭</el-button>
      </div>
    </el-dialog>

    <!-- 解密下载-先校验哈希，正确才下载 -->
    <el-dialog title="解密下载（先校验哈希）" :visible.sync="downloadDialog.open" width="500px" append-to-body>
      <el-form label-width="100px" label-position="left">
        <el-alert title="请先输入或上传文件对应的 SHA256 哈希值，校验通过后才可下载" type="warning" :closable="false" show-icon style="margin-bottom: 15px;" />
        <el-form-item label="哈希值" required>
          <el-input v-model="downloadDialog.verifyHash" type="textarea" :rows="3" placeholder="请输入 SHA256 哈希值（十六进制），校验通过后才可下载" clearable />
        </el-form-item>
        <el-form-item label="上传哈希文件">
          <el-upload
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleHashFileChange"
            :on-remove="() => downloadDialog.verifyHash = ''"
            accept=".txt,.hash"
          >
            <el-button size="small" type="primary">选择哈希文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="confirmDownload">确认下载</el-button>
        <el-button @click="downloadDialog.open = false">取 消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { listFile, downloadFile, delFiles, getFileHash } from '@/api/encry/file'
import { getKeyInfo } from '@/api/encry/key'
import { addDateRange } from "@/utils/ruoyi";

export default {
  name: 'EncryFile',
  data() {
    return {
      loading: true,
      ids: [],
      single: true,
      multiple: true,
      showSearch: true,
      total: 0,
      fileList: [],
      dateRange: [],
      queryParams: {
        pageNum: 1,
        pageSize: 10,
        originalName: undefined,
        encryptAlgo: undefined
      },
      upload: {
        open: false,
        title: '加密上传',
        encryptAlgo: 'AES',
        aesMode: 'CBC',
        userKey: '',
        key: 0
      },
      hashDialog: { open: false, content: '' },
      downloadDialog: { open: false, verifyHash: '', fileId: null, filename: '' }
    }
  },
  computed: {
    uploadAction() {
      return process.env.VUE_APP_BASE_API + '/encry/file/upload'
    },
    uploadFormData() {
      const d = {
        encryptAlgo: this.upload.encryptAlgo,
        aesMode: this.upload.encryptAlgo === 'AES' ? this.upload.aesMode : 'CBC'
      }
      if (this.upload.userKey && this.upload.userKey.trim()) {
        d.userKey = this.upload.userKey.trim()
      }
      return d
    }
  },
  created() {
    this.getList()
  },
  methods: {
    /** 查询文件列表 */
    getList() {
      this.loading = true
      listFile(addDateRange(this.queryParams, this.dateRange)).then(response => {
        this.fileList = response.rows
        this.total = response.total
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    getRowKey(row) {
      return row.fileId ?? row.file_id ?? (row.originalName || row.original_name || '') + '_' + (row.createTime || row.create_time || '')
    },
    formatSize(bytes) {
      if (!bytes) return '0.0 MB'
      const mb = bytes / (1024 * 1024)
      return mb.toFixed(1) + ' MB'
    },
    handleQuery() {
      this.queryParams.pageNum = 1
      this.getList()
    },
    resetQuery() {
      this.resetForm('queryForm')
      this.handleQuery()
    },
    handleSelectionChange(selection) {
      this.ids = selection.map(item => item.fileId ?? item.file_id)
      this.single = selection.length !== 1
      this.multiple = !selection.length
    },
    handleUpload() {
      getKeyInfo().then(res => {
        const data = res.data || res
        if (!data || !(data.keyId || data.key_id)) {
          this.$modal.msgWarning('请先生成 RSA 密钥对，请在【密钥管理】中先生成')
          return
        }
        this.upload.aesMode = 'CBC'
        this.upload.userKey = ''
        this.upload.key++
        this.upload.open = true
      }).catch(() => {})
    },
    generateRandomKey() {
      const arr = new Uint8Array(32)
      crypto.getRandomValues(arr)
      this.upload.userKey = Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('')
    },
    handleUploadSuccess(res) {
      this.$modal.msgSuccess('上传成功')
      this.upload.open = false
      this.getList()
      const data = res.data || res
      const hash = data.fileHash || data.file_hash || ''
      if (hash) {
        this.hashDialog.content = hash
        this.hashDialog.open = true
      }
    },
    handleUploadError() {
      // 上传失败时由 FileUpload 显示错误，此处不关闭对话框，方便用户重试
    },
    handleDownload(row) {
      this.downloadDialog.fileId = row.fileId ?? row.file_id
      this.downloadDialog.filename = row.originalName ?? row.original_name
      this.downloadDialog.verifyHash = ''
      this.downloadDialog.open = true
    },
    handleHashFileChange(file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        this.downloadDialog.verifyHash = (e.target.result || '').trim()
      }
      reader.readAsText(file.raw)
    },
    confirmDownload() {
      const { fileId, filename, verifyHash } = this.downloadDialog
      const hash = verifyHash ? verifyHash.trim() : ''
      if (!hash) {
        this.$modal.msgWarning('请输入哈希值进行校验后再下载')
        return
      }
      // 先校验哈希：获取服务端存储的哈希，一致才允许下载
      getFileHash(fileId).then(res => {
        const data = res.data || res
        const storedHash = (data.fileHash || data.file_hash || '').trim().toLowerCase()
        const inputHash = hash.toLowerCase()
        if (!storedHash) {
          this.$modal.msgWarning('该文件暂无哈希值（可能是早期上传），无法校验，请重新上传以生成')
          return
        }
        if (storedHash !== inputHash) {
          this.$modal.msgError('哈希值不正确，无法下载')
          return
        }
        // 校验通过，再发起解密下载
        downloadFile(fileId, filename, hash).then(() => {
          this.$modal.msgSuccess('下载成功')
          this.downloadDialog.open = false
        }).catch((err) => {
          this.$modal.msgError(err && err.message ? err.message : '下载失败')
        })
      }).catch(() => {
        this.$modal.msgError('获取文件哈希失败，无法校验')
      })
    },
    copyHash() {
      const content = this.hashDialog.content
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(content).then(() => {
          this.$modal.msgSuccess('已复制到剪贴板')
        })
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = content
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        this.$modal.msgSuccess('已复制到剪贴板')
      }
    },
    handleGetHash(row) {
      const fileId = row.fileId ?? row.file_id
      getFileHash(fileId).then(res => {
        const data = res.data || res
        const hash = data.fileHash || data.file_hash || ''
        if (hash) {
          this.hashDialog.content = hash
          this.hashDialog.open = true
        } else {
          this.$modal.msgWarning('该文件暂无哈希值（可能是早期上传），请重新上传以生成')
        }
      }).catch(() => {})
    },
    exportHashFile() {
      const content = this.hashDialog.content
      const blob = new Blob([content], { type: 'text/plain' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'file_hash.txt'
      a.click()
      URL.revokeObjectURL(a.href)
      this.$modal.msgSuccess('已导出哈希文件')
    },
    handleDelete(row) {
      const id = row?.fileId ?? row?.file_id
      const fileIds = id ? [id] : this.ids
      this.$modal.confirm('是否确认删除所选文件？').then(() => {
        return delFiles(fileIds)
      }).then(() => {
        this.getList()
        this.$modal.msgSuccess('删除成功')
      }).catch(() => {})
    }
  }
}
</script>
