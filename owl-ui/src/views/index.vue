<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :lg="24">
        <div class="welcome-section">
          <div class="welcome-content">
            <div class="welcome-title">
              <svg-icon icon-class="dashboard" class-name="welcome-icon" />
              <span>欢迎使用文件加解密系统</span>
            </div>
            <div class="welcome-subtitle">
              文件加密存储与解密平台
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 功能统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="12" :lg="6" v-for="(stat, index) in statsData" :key="index">
        <div class="stat-card" @click="goToPage(stat.path)">
          <div class="stat-icon" :style="{ backgroundColor: stat.bgColor, color: stat.iconColor }">
            <svg-icon :icon-class="stat.icon" class-name="stat-icon-inner" />
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :lg="24">
        <div class="quick-access-wrapper">
          <div class="quick-access-title">
            <svg-icon icon-class="link" class-name="title-icon" />
            <span>快捷入口</span>
          </div>
          <el-row :gutter="20" class="quick-access-cards">
            <el-col :xs="12" :sm="12" :md="6" :lg="6" v-for="item in quickAccessItems" :key="item.name">
              <div class="quick-access-card" @click="goToPage(item.path)">
                <div class="card-icon" :style="{ backgroundColor: item.color }">
                  <svg-icon :icon-class="item.icon" class-name="card-icon-inner" />
                </div>
                <div class="card-info">
                  <div class="card-title">{{ item.title }}</div>
                  <div class="card-desc">{{ item.desc }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-col>
    </el-row>

    <!-- 系统介绍 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="info-card">
          <div class="info-title">
            <svg-icon icon-class="documentation" class-name="info-icon" />
            <span>系统功能</span>
          </div>
          <div class="info-content">
            <div class="feature-item" v-for="(feature, index) in systemFeatures" :key="index">
              <div class="feature-dot" :style="{ backgroundColor: feature.color }"></div>
              <div class="feature-text">
                <div class="feature-name">{{ feature.name }}</div>
                <div class="feature-desc">{{ feature.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="12">
        <div class="info-card">
          <div class="info-title">
            <svg-icon icon-class="lock" class-name="info-icon" />
            <span>安全保障</span>
          </div>
          <div class="info-content">
            <div class="security-item" v-for="(item, index) in securityItems" :key="index">
              <div class="security-icon">
                <svg-icon :icon-class="item.icon" />
              </div>
              <div class="security-text">
                <div class="security-name">{{ item.name }}</div>
                <div class="security-desc">{{ item.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'Index',
  data() {
    return {
      // 统计数据 - 使用静态数据，不依赖后端接口
      statsData: [
        {
          value: 'AES/DES',
          label: '对称加密',
          icon: 'password',
          bgColor: '#e8f4f8',
          iconColor: '#40c9c6',
          path: '/encry/file'
        },
        {
          value: 'RSA',
          label: '非对称加密',
          icon: 'key',
          bgColor: '#e6f7ff',
          iconColor: '#36a3f7',
          path: '/encry/key'
        },
        {
          value: 'SHA256',
          label: '哈希校验',
          icon: 'validCode',
          bgColor: '#fff0f6',
          iconColor: '#f4516c',
          path: '/encry/file'
        },
        {
          value: '安全',
          label: '存储保护',
          icon: 'lock',
          bgColor: '#f6ffed',
          iconColor: '#34bfa3',
          path: '/user/profile'
        }
      ],
      // 快捷入口
      quickAccessItems: [
        {
          name: 'file',
          title: '加密文件管理',
          desc: '上传、下载、管理加密文件',
          icon: 'documentation',
          color: '#40c9c6',
          path: '/encry/file'
        },
        {
          name: 'key',
          title: '密钥管理',
          desc: '生成、管理RSA密钥对',
          icon: 'key',
          color: '#36a3f7',
          path: '/encry/key'
        },
        {
          name: 'notice',
          title: '通知公告',
          desc: '查看系统通知和公告信息',
          icon: 'message',
          color: '#f4516c',
          path: '/system/notice'
        },
        {
          name: 'profile',
          title: '个人中心',
          desc: '查看个人信息和文件统计',
          icon: 'user',
          color: '#34bfa3',
          path: '/user/profile'
        }
      ],
      // 系统功能
      systemFeatures: [
        {
          name: '混合加密',
          desc: '文件使用AES/DES对称加密，密钥使用RSA非对称加密保护',
          color: '#40c9c6'
        },
        {
          name: '哈希校验',
          desc: '支持SHA256哈希值计算，确保文件完整性',
          color: '#36a3f7'
        },
        {
          name: '密钥管理',
          desc: '安全的RSA密钥对生成和管理机制',
          color: '#f4516c'
        },
        {
          name: '访问控制',
          desc: '基于角色的权限管理系统',
          color: '#34bfa3'
        }
      ],
      // 安全保障
      securityItems: [
        {
          name: '端到端加密',
          desc: '文件在传输和存储过程中全程加密保护',
          icon: 'password'
        },
        {
          name: '密钥分离',
          desc: '加密密钥与存储分离，增强安全性',
          icon: 'key'
        },
        {
          name: '完整性校验',
          desc: '下载时自动校验文件哈希值',
          icon: 'validCode'
        },
        {
          name: '访问审计',
          desc: '记录用户操作日志，可追溯审计',
          icon: 'log'
        }
      ]
    }
  },
  methods: {
    goToPage(path) {
      this.$router.push(path)
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

.dashboard-container {
  padding: 24px;
  background-color: $grey-50;
  position: relative;
  min-height: calc(100vh - 84px);

  // 欢迎区域
  .welcome-section {
    background: linear-gradient(135deg, $grey-700 0%, $grey-800 100%);
    border-radius: 12px;
    padding: 32px;
    margin-bottom: 24px;
    box-shadow: 0 4px 12px rgba($grey-950, 0.1);

    .welcome-content {
      text-align: center;

      .welcome-title {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 12px;

        .welcome-icon {
          font-size: 32px;
          margin-right: 12px;
        }
      }

      .welcome-subtitle {
        font-size: 14px;
        color: $grey-300;
      }
    }
  }

  // 统计卡片
  .stats-row {
    margin-bottom: 24px;

    .stat-card {
      background: #ffffff;
      border-radius: 12px;
      padding: 24px;
      display: flex;
      align-items: center;
      box-shadow: 0 2px 8px rgba($grey-950, 0.04);
      border: 1px solid $grey-100;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba($grey-950, 0.08);
      }

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        flex-shrink: 0;

        .stat-icon-inner {
          font-size: 28px;
        }
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 20px;
          font-weight: 600;
          color: $grey-900;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 13px;
          color: $grey-500;
        }
      }
    }
  }

  // 快捷入口
  .quick-access-wrapper {
    background: #ffffff;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba($grey-950, 0.04);
    border: 1px solid $grey-100;

    .quick-access-title {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 600;
      color: $grey-900;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid $grey-100;

      .title-icon {
        font-size: 18px;
        margin-right: 10px;
        color: $grey-600;
      }
    }

    .quick-access-cards {
      .quick-access-card {
        display: flex;
        align-items: center;
        padding: 20px;
        margin-bottom: 16px;
        border-radius: 12px;
        background: $grey-50;
        border: 1px solid $grey-100;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba($grey-950, 0.08);
          background: #ffffff;
          border-color: $grey-200;
        }

        .card-icon {
          width: 48px;
          height: 48px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 14px;
          flex-shrink: 0;

          .card-icon-inner {
            font-size: 24px;
            color: #ffffff;
          }
        }

        .card-info {
          flex: 1;

          .card-title {
            font-size: 15px;
            font-weight: 600;
            color: $grey-900;
            margin-bottom: 4px;
          }

          .card-desc {
            font-size: 12px;
            color: $grey-500;
            line-height: 1.4;
          }
        }
      }
    }
  }

  // 信息卡片
  .info-card {
    background: #ffffff;
    padding: 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba($grey-950, 0.04);
    border: 1px solid $grey-100;
    height: calc(100% - 24px);

    .info-title {
      display: flex;
      align-items: center;
      font-size: 16px;
      font-weight: 600;
      color: $grey-900;
      margin-bottom: 20px;
      padding-bottom: 16px;
      border-bottom: 1px solid $grey-100;

      .info-icon {
        font-size: 18px;
        margin-right: 10px;
        color: $grey-600;
      }
    }

    .info-content {
      .feature-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 16px;

        &:last-child {
          margin-bottom: 0;
        }

        .feature-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin-right: 12px;
          margin-top: 6px;
          flex-shrink: 0;
        }

        .feature-text {
          flex: 1;

          .feature-name {
            font-size: 14px;
            font-weight: 500;
            color: $grey-800;
            margin-bottom: 4px;
          }

          .feature-desc {
            font-size: 12px;
            color: $grey-500;
            line-height: 1.5;
          }
        }
      }

      .security-item {
        display: flex;
        align-items: flex-start;
        margin-bottom: 16px;
        padding: 12px;
        background: $grey-50;
        border-radius: 8px;

        &:last-child {
          margin-bottom: 0;
        }

        .security-icon {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          background: $grey-200;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 12px;
          flex-shrink: 0;

          .svg-icon {
            font-size: 18px;
            color: $grey-600;
          }
        }

        .security-text {
          flex: 1;

          .security-name {
            font-size: 14px;
            font-weight: 500;
            color: $grey-800;
            margin-bottom: 4px;
          }

          .security-desc {
            font-size: 12px;
            color: $grey-500;
            line-height: 1.5;
          }
        }
      }
    }
  }
}

@media (max-width: 1024px) {
  .dashboard-container {
    padding: 16px;

    .welcome-section {
      padding: 24px;

      .welcome-content {
        .welcome-title {
          font-size: 20px;

          .welcome-icon {
            font-size: 28px;
          }
        }
      }
    }

    .stat-card {
      padding: 16px;

      .stat-icon {
        width: 48px;
        height: 48px;

        .stat-icon-inner {
          font-size: 24px;
        }
      }

      .stat-info {
        .stat-value {
          font-size: 16px;
        }
      }
    }

    .quick-access-wrapper {
      padding: 16px;

      .quick-access-cards {
        .quick-access-card {
          padding: 16px;

          .card-icon {
            width: 40px;
            height: 40px;

            .card-icon-inner {
              font-size: 20px;
            }
          }
        }
      }
    }

    .info-card {
      padding: 16px;
      height: auto;
    }
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    .welcome-section {
      .welcome-content {
        .welcome-title {
          flex-direction: column;

          .welcome-icon {
            margin-right: 0;
            margin-bottom: 8px;
          }
        }
      }
    }

    .stat-card {
      flex-direction: column;
      text-align: center;

      .stat-icon {
        margin-right: 0;
        margin-bottom: 12px;
      }
    }

    .quick-access-cards {
      .quick-access-card {
        flex-direction: column;
        text-align: center;

        .card-icon {
          margin-right: 0;
          margin-bottom: 12px;
        }
      }
    }
  }
}
</style>
