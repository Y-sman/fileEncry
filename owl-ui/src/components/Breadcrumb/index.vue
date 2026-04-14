<template>
  <el-breadcrumb class="app-breadcrumb" separator="/">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item v-for="(item,index) in levelList" :key="item.path">
        <span v-if="item.redirect === 'noRedirect' || index == levelList.length - 1" class="no-redirect">{{ item.meta.title }}</span>
        <a v-else @click.prevent="handleLink(item)">{{ item.meta.title }}</a>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script>
export default {
  data() {
    return {
      levelList: null
    }
  },
  watch: {
    $route(route) {
      // if you go to the redirect page, do not update the breadcrumbs
      if (route.path.startsWith('/redirect/')) {
        return
      }
      this.getBreadcrumb()
    }
  },
  created() {
    this.getBreadcrumb()
  },
  methods: {
    getBreadcrumb() {
      // only show routes with meta.title
      let matched = this.$route.matched.filter(item => item.meta && item.meta.title)
      const first = matched[0]

      if (!this.isDashboard(first)) {
        matched = [{ path: '/index', meta: { title: '首页' }}].concat(matched)
      }

      this.levelList = matched.filter(item => item.meta && item.meta.title && item.meta.breadcrumb !== false)
    },
    isDashboard(route) {
      const name = route && route.name
      if (!name) {
        return false
      }
      return name.trim() === 'Index'
    },
    handleLink(item) {
      const { redirect, path } = item
      if (redirect) {
        this.$router.push(redirect)
        return
      }
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

.app-breadcrumb.el-breadcrumb {
  display: inline-flex;
  align-items: center;
  font-size: 14px;
  line-height: 44px;
  margin-left: 0;

  ::v-deep .el-breadcrumb__item {
    .el-breadcrumb__inner {
      color: $grey-500;
      font-weight: 400;
      transition: color 0.2s ease;

      a {
        color: $grey-600;
        font-weight: 500;

        &:hover {
          color: $grey-900;
        }
      }
    }

    &:last-child .el-breadcrumb__inner {
      color: $grey-900;
      font-weight: 600;
    }

    .el-breadcrumb__separator {
      color: $grey-300;
      margin: 0 8px;
    }
  }

  .no-redirect {
    color: $grey-900;
    cursor: text;
    font-weight: 600;
  }
}

// Breadcrumb transition animation
.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.3s ease;
}

.breadcrumb-enter,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(10px);
}

.breadcrumb-move {
  transition: all 0.3s ease;
}
</style>
