<template>
  <div class="navbar">
    <!-- 上层：工具栏 -->
    <div class="navbar-top">
      <hamburger id="hamburger-container" :is-active="sidebar.opened" class="hamburger-container" @toggleClick="toggleSideBar" />

      <div class="right-menu">
        <template v-if="device!=='mobile'">
          <search id="header-search" class="right-menu-item" />

          <screenfull id="screenfull" class="right-menu-item hover-effect" />

          <el-tooltip content="布局大小" effect="dark" placement="bottom">
            <size-select id="size-select" class="right-menu-item hover-effect" />
          </el-tooltip>

        </template>

        <el-dropdown class="avatar-container right-menu-item hover-effect" trigger="click">
          <div class="avatar-wrapper">
            <img :src="avatar" class="user-avatar">
            <i class="el-icon-caret-bottom" />
          </div>
          <el-dropdown-menu slot="dropdown">
            <router-link to="/user/profile">
              <el-dropdown-item>个人中心</el-dropdown-item>
            </router-link>
            <el-dropdown-item @click.native="setting = true">
              <span>布局设置</span>
            </el-dropdown-item>
            <el-dropdown-item divided @click.native="logout">
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!-- 下层：面包屑 -->
    <div class="navbar-bottom" v-if="!topNav">
      <i class="el-icon-location-outline breadcrumb-icon"></i>
      <breadcrumb id="breadcrumb-container" class="breadcrumb-container" />
    </div>
    <top-nav id="topmenu-container" class="topmenu-container" v-if="topNav"/>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Breadcrumb from '@/components/Breadcrumb'
import TopNav from '@/components/TopNav'
import Hamburger from '@/components/Hamburger'
import Screenfull from '@/components/Screenfull'
import SizeSelect from '@/components/SizeSelect'
import Search from '@/components/HeaderSearch'
import RuoYiGit from '@/components/RuoYi/Git'
import RuoYiDoc from '@/components/RuoYi/Doc'

export default {
  components: {
    Breadcrumb,
    TopNav,
    Hamburger,
    Screenfull,
    SizeSelect,
    Search,
    RuoYiGit,
    RuoYiDoc
  },
  computed: {
    ...mapGetters([
      'sidebar',
      'avatar',
      'device'
    ]),
    setting: {
      get() {
        return this.$store.state.settings.showSettings
      },
      set(val) {
        this.$store.dispatch('settings/changeSetting', {
          key: 'showSettings',
          value: val
        })
      }
    },
    topNav: {
      get() {
        return this.$store.state.settings.topNav
      }
    }
  },
  methods: {
    toggleSideBar() {
      this.$store.dispatch('app/toggleSideBar')
    },
    async logout() {
      this.$confirm('确定注销并退出系统吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$store.dispatch('LogOut').then(() => {
          location.href = '/index';
        })
      }).catch(() => {});
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

.navbar {
  overflow: hidden;
  position: relative;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba($grey-950, 0.04);
  border-bottom: 1px solid $grey-100;

  // 上层工具栏
  .navbar-top {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid $grey-100;

    .hamburger-container {
      height: 100%;
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 0 16px;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      -webkit-tap-highlight-color: transparent;
      color: $grey-600;

      &:hover {
        background: $grey-50;
        color: $grey-900;
      }
    }

    .right-menu {
      height: 100%;
      display: flex;
      align-items: center;
      padding-right: 16px;

      &:focus {
        outline: none;
      }

      .right-menu-item {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0 12px;
        height: 100%;
        font-size: 18px;
        color: $grey-500;
        vertical-align: text-bottom;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

        &.hover-effect {
          cursor: pointer;

          &:hover {
            color: $grey-900;
            background: $grey-50;
          }
        }
      }

      .avatar-container {
        margin-right: 8px;
        margin-left: 8px;

        .avatar-wrapper {
          position: relative;
          display: flex;
          align-items: center;

          .user-avatar {
            cursor: pointer;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            border: 2px solid $grey-100;
            transition: all 0.25s ease;

            &:hover {
              border-color: $grey-300;
            }
          }

          .el-icon-caret-bottom {
            cursor: pointer;
            position: absolute;
            right: -16px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 12px;
            color: $grey-400;
            transition: color 0.2s ease;

            &:hover {
              color: $grey-700;
            }
          }
        }
      }
    }
  }

  // 下层面包屑
  .navbar-bottom {
    height: 44px;
    background: $grey-50;
    display: flex;
    align-items: center;
    padding: 0 16px;

    .breadcrumb-icon {
      color: $grey-500;
      font-size: 14px;
      margin-right: 8px;
    }

    .breadcrumb-container {
      line-height: 44px;
    }
  }

  .topmenu-container {
    position: absolute;
    left: 50px;
    top: 50px;
  }

  .errLog-container {
    display: inline-block;
    vertical-align: top;
  }
}
</style>
