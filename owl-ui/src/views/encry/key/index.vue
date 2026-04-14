<template>
  <div class="app-container">
    <el-card v-loading="loading">
      <div slot="header" class="clearfix">
        <span>RSA 密钥管理</span>
        <el-button
          style="float: right;"
          type="primary"
          size="small"
          icon="el-icon-plus"
          @click="handleGenerate"
          v-hasPermi="['encry:key:add']"
          :disabled="!!keyInfo"
        >{{ keyInfo ? '已生成密钥' : '生成密钥' }}</el-button>
      </div>

      <el-empty v-if="!keyInfo && !loading" description="您尚未生成 RSA 密钥对，请先生成后再使用文件加密功能（文件将使用 AES/DES 加密，密钥由 RSA 保护）">
        <el-button type="primary" @click="handleGenerate" v-hasPermi="['encry:key:add']">生成密钥</el-button>
      </el-empty>

      <el-descriptions v-else-if="keyInfo" :column="1" border>
        <el-descriptions-item label="算法类型">RSA 非对称加密</el-descriptions-item>
        <el-descriptions-item label="密钥ID">{{ keyInfo.keyId || keyInfo.key_id }}</el-descriptions-item>
        <el-descriptions-item label="RSA 密钥长度">{{ keyInfo.keySize || keyInfo.key_size }} 位</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="keyInfo.status === '0' ? 'success' : 'danger'">
            {{ keyInfo.status === '0' ? '正常' : '停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ parseTime(keyInfo.createTime || keyInfo.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="操作">
          <el-button size="mini" type="text" icon="el-icon-download" @click="handleExportPublic" v-hasPermi="['encry:key:export']">导出公钥</el-button>
          <el-button size="mini" type="text" icon="el-icon-download" @click="handleExportPrivate" v-hasPermi="['encry:key:export']" style="color: #F56C6C;">导出私钥</el-button>
        </el-descriptions-item>
      </el-descriptions>

      <template v-if="keyInfo">
        <el-card shadow="never" style="margin-top: 16px;">
          <div slot="header" class="clearfix">
            <span>查看公钥</span>
            <el-button size="small" type="text" icon="el-icon-view" @click="loadPublicKey" :loading="publicKeyLoading">加载公钥</el-button>
            <el-button size="small" type="text" icon="el-icon-document-copy" @click="copyPublicKey" :disabled="!publicKeyText">复制</el-button>
          </div>
          <el-input v-if="publicKeyText" type="textarea" :value="publicKeyText" :rows="6" readonly />
          <span v-else class="text-muted">点击「加载公钥」后显示</span>
        </el-card>
        <el-card shadow="never" style="margin-top: 16px;">
          <div slot="header" class="clearfix">
            <span>查看私钥</span>
            <el-button size="small" type="text" icon="el-icon-view" @click="loadPrivateKey" :loading="privateKeyLoading">加载私钥</el-button>
            <el-button size="small" type="text" :icon="showPrivatePlain ? 'el-icon-hide' : 'el-icon-view'" @click="showPrivatePlain = !showPrivatePlain" :disabled="!privateKeyText">{{ showPrivatePlain ? '掩码显示' : '显示明文' }}</el-button>
            <el-button size="small" type="text" icon="el-icon-document-copy" @click="copyPrivateKey" :disabled="!privateKeyText">复制</el-button>
            <el-button size="small" type="text" icon="el-icon-download" @click="downloadPrivateKeyFile" :disabled="!privateKeyText" style="color: #F56C6C;">下载为文件</el-button>
          </div>
          <el-input
            v-if="privateKeyText"
            type="textarea"
            :value="showPrivatePlain ? privateKeyText : maskedPrivateKey"
            :rows="6"
            readonly
          />
          <span v-else class="text-muted">点击「加载私钥」后显示（默认掩码，可切换明文）</span>
        </el-card>
      </template>

      <el-alert
        title="混合加密说明"
        type="info"
        :closable="false"
        style="margin-top: 20px;"
      >
        <template slot="default">
          <p><b>RSA</b> 用于加密/解密文件时使用的对称密钥（AES/DES），保障密钥传输与存储安全。</p>
          <p>1. RSA 私钥请妥善保管，切勿泄露</p>
          <p>2. 私钥用于解密对称密钥，丢失后将无法恢复加密文件</p>
          <p>3. 建议定期备份 RSA 公钥和私钥</p>
        </template>
      </el-alert>
    </el-card>

    <!-- 公钥/私钥展示对话框（导出时弹窗） -->
    <el-dialog :title="exportDialog.title" :visible.sync="exportDialog.open" width="700px" append-to-body>
      <el-input
        type="textarea"
        :value="exportDialog.content"
        :rows="12"
        readonly
      />
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="copyToClipboard">复 制</el-button>
        <el-button v-if="exportDialog.isPrivate" type="danger" plain @click="downloadPrivateFromDialog">下载为文件</el-button>
        <el-button @click="exportDialog.open = false">关 闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getKeyInfo, generateKey, exportPublicKey, exportPrivateKey } from '@/api/encry/key'

export default {
  name: 'EncryKey',
  data() {
    return {
      loading: false,
      keyInfo: null,
      publicKeyText: '',
      publicKeyLoading: false,
      privateKeyText: '',
      privateKeyLoading: false,
      showPrivatePlain: false,
      exportDialog: {
        open: false,
        title: '',
        content: '',
        isPrivate: false
      }
    }
  },
  computed: {
    maskedPrivateKey() {
      if (!this.privateKeyText || this.privateKeyText.length < 80) return '*** (已掩码) ***'
      return this.privateKeyText.slice(0, 40) + '\n... (已掩码，点击「显示明文」查看) ...\n' + this.privateKeyText.slice(-40)
    }
  },
  created() {
    this.loadKeyInfo()
  },
  methods: {
    loadKeyInfo() {
      this.loading = true
      getKeyInfo().then(response => {
        this.keyInfo = response.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleGenerate() {
      this.$prompt('请输入 RSA 密钥长度', '生成 RSA 密钥对', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: '2048',
        inputPattern: /^(2048|4096)$/,
        inputErrorMessage: '请输入 2048 或 4096'
      }).then(({ value }) => {
        this.loading = true
        return generateKey(parseInt(value) || 2048)
      }).then(response => {
        this.$modal.msgSuccess('RSA 密钥对生成成功')
        this.loadKeyInfo()
      }).catch(() => {}).finally(() => {
        this.loading = false
      })
    },
    loadPublicKey() {
      this.publicKeyLoading = true
      exportPublicKey().then(res => {
        const d = res.data || res
        this.publicKeyText = d.publicKey || d.public_key || ''
      }).finally(() => { this.publicKeyLoading = false })
    },
    loadPrivateKey() {
      this.$modal.confirm('私钥极其敏感，加载后请勿泄露。确认加载？').then(() => {
        this.privateKeyLoading = true
        this.showPrivatePlain = false
        return exportPrivateKey()
      }).then(res => {
        const d = res.data || res
        this.privateKeyText = d.privateKey || d.private_key || ''
      }).catch(() => {}).finally(() => { this.privateKeyLoading = false })
    },
    copyPublicKey() {
      this.copyText(this.publicKeyText)
    },
    copyPrivateKey() {
      this.copyText(this.privateKeyText)
    },
    downloadPrivateKeyFile() {
      if (!this.privateKeyText) return
      const blob = new Blob([this.privateKeyText], { type: 'application/x-pem-file' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'rsa_private.pem'
      a.click()
      URL.revokeObjectURL(a.href)
      this.$modal.msgSuccess('私钥已下载')
    },
    downloadPrivateFromDialog() {
      const content = this.exportDialog.content
      if (!content) return
      const blob = new Blob([content], { type: 'application/x-pem-file' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'rsa_private.pem'
      a.click()
      URL.revokeObjectURL(a.href)
      this.$modal.msgSuccess('私钥已下载')
      this.exportDialog.open = false
    },
    handleExportPublic() {
      exportPublicKey().then(response => {
        this.exportDialog.title = 'RSA 公钥 (PEM 格式)'
        this.exportDialog.content = response.data?.publicKey || response.data?.public_key || ''
        this.exportDialog.isPrivate = false
        this.exportDialog.open = true
      })
    },
    handleExportPrivate() {
      this.$modal.confirm('私钥极其敏感，导出后请妥善保管。确认导出？').then(() => {
        return exportPrivateKey()
      }).then(response => {
        this.exportDialog.title = 'RSA 私钥 (PEM 格式) - 请妥善保管'
        this.exportDialog.content = response.data?.privateKey || response.data?.private_key || ''
        this.exportDialog.isPrivate = true
        this.exportDialog.open = true
      }).catch(() => {})
    },
    copyText(text) {
      if (!text) return
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => this.$modal.msgSuccess('已复制到剪贴板'))
      } else {
        const ta = document.createElement('textarea')
        ta.value = text
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        this.$modal.msgSuccess('已复制到剪贴板')
      }
    },
    copyToClipboard() {
      this.copyText(this.exportDialog.content)
    }
  }
}
</script>
