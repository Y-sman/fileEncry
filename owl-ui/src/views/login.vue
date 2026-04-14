<template>
  <div class="login">
    <el-form ref="loginForm" :model="loginForm" :rules="loginRules" class="login-form">
      <h3 class="title">文件加解密系统</h3>
      <el-form-item prop="username">
        <el-input
          v-model="loginForm.username"
          type="text"
          auto-complete="off"
          placeholder="用户名/邮箱"
        >
          <svg-icon slot="prefix" icon-class="user" class="el-input__icon input-icon" />
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          auto-complete="off"
          placeholder="密码"
          @keyup.enter.native="handleLogin"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" />
        </el-input>
      </el-form-item>
      <el-form-item prop="code" v-if="captchaOnOff">
        <el-input
          v-model="loginForm.code"
          auto-complete="off"
          placeholder="验证码"
          style="width: 63%"
          @keyup.enter.native="handleLogin"
        >
          <svg-icon slot="prefix" icon-class="validCode" class="el-input__icon input-icon" />
        </el-input>
        <div class="login-code">
          <img :src="codeUrl" @click="getCode" class="login-code-img"/>
        </div>
      </el-form-item>
      <el-checkbox v-model="loginForm.rememberMe" style="margin:0px 0px 25px 0px;">记住密码</el-checkbox>
      <el-form-item style="width:100%;">
        <el-button
          :loading="loading"
          size="medium"
          type="primary"
          style="width:100%;"
          @click.native.prevent="handleLogin"
        >
          <span v-if="!loading">登 录</span>
          <span v-else>登 录 中...</span>
        </el-button>
        <div style="float: right;" v-if="register">
          <router-link class="link-type" :to="'/register'">立即注册</router-link>
        </div>
      </el-form-item>
    </el-form>
    <!--  底部  -->
    <div class="el-login-footer">
<!--      <span>Copyright © 2018-2022 test.vip All Rights Reserved.</span>-->
    </div>
  </div>
</template>

<script>
import { getCodeImg } from "@/api/login";
import Cookies from "js-cookie";
import { encrypt, decrypt } from '@/utils/jsencrypt'

export default {
  name: "Login",
  data() {
    return {
      codeUrl: "",
      loginForm: {
        username: "admin",
        password: "admin123",
        rememberMe: false,
        code: "",
        uuid: ""
      },
      loginRules: {
        username: [
          { required: true, trigger: "blur", message: "请输入您的账号" }
        ],
        password: [
          { required: true, trigger: "blur", message: "请输入您的密码" }
        ],
        code: [{ required: true, trigger: "change", message: "请输入验证码" }]
      },
      loading: false,
      // 验证码开关
      captchaOnOff: true,
      // 注册开关
      register: true,
      redirect: undefined
    };
  },
  watch: {
    $route: {
      handler: function(route) {
        this.redirect = route.query && route.query.redirect;
      },
      immediate: true
    }
  },
  created() {
    this.getCode();
    this.getCookie();
  },
  methods: {
    getCode() {
      getCodeImg().then(res => {
        this.captchaOnOff = res.captchaOnOff === undefined ? true : res.captchaOnOff;
        if (this.captchaOnOff) {
          this.codeUrl = "data:image/gif;base64," + res.img;
          this.loginForm.uuid = res.uuid;
        }
      });
    },
    getCookie() {
      const username = Cookies.get("username");
      const password = Cookies.get("password");
      const rememberMe = Cookies.get('rememberMe')
      this.loginForm = {
        username: username === undefined ? this.loginForm.username : username,
        password: password === undefined ? this.loginForm.password : decrypt(password),
        rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
      };
    },
    handleLogin() {
      this.$refs.loginForm.validate(valid => {
        if (valid) {
          this.loading = true;
          if (this.loginForm.rememberMe) {
            Cookies.set("username", this.loginForm.username, { expires: 30 });
            Cookies.set("password", encrypt(this.loginForm.password), { expires: 30 });
            Cookies.set('rememberMe', this.loginForm.rememberMe, { expires: 30 });
          } else {
            Cookies.remove("username");
            Cookies.remove("password");
            Cookies.remove('rememberMe');
          }
          this.$store.dispatch("Login", this.loginForm).then(() => {
            this.$router.push({ path: this.redirect || "/" }).catch(()=>{});
          }).catch(() => {
            this.loading = false;
            if (this.captchaOnOff) {
              this.getCode();
            }
          });
        }
      });
    }
  }
};
</script>

<style rel="stylesheet/scss" lang="scss">
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

.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: linear-gradient(135deg, $grey-100 0%, $grey-50 50%, #ffffff 100%);
  position: relative;
  overflow: hidden;

  // 极简装饰性背景元素
  &::before {
    content: '';
    position: absolute;
    width: 800px;
    height: 800px;
    background: radial-gradient(circle, rgba($grey-400, 0.06) 0%, transparent 70%);
    top: -300px;
    right: -300px;
    border-radius: 50%;
  }

  &::after {
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba($grey-300, 0.04) 0%, transparent 70%);
    bottom: -200px;
    left: -200px;
    border-radius: 50%;
  }
}

.title {
  margin: 0 auto 40px auto;
  text-align: center;
  font-size: 28px;
  font-weight: 600;
  color: $grey-900;
  letter-spacing: 3px;
}

.login-form {
  border-radius: 20px;
  background: #ffffff;
  width: 420px;
  padding: 48px 40px 32px 40px;
  box-shadow: 0 4px 24px rgba($grey-950, 0.06), 0 1px 4px rgba($grey-950, 0.04);
  border: 1px solid $grey-100;
  position: relative;
  z-index: 1;

  .el-input {
    height: 48px;

    input {
      height: 48px;
      border-radius: 12px;
      border: 1px solid $grey-200;
      padding-left: 48px;
      font-size: 15px;
      background-color: $grey-50;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        border-color: $grey-300;
        background-color: #ffffff;
      }

      &:focus {
        border-color: $grey-600;
        background-color: #ffffff;
        box-shadow: 0 0 0 4px rgba($grey-600, 0.08);
      }

      &::placeholder {
        color: $grey-400;
      }
    }
  }

  .input-icon {
    height: 48px;
    width: 20px;
    margin-left: 16px;
    color: $grey-400;
  }

  .el-form-item {
    margin-bottom: 24px;
  }

  .el-button--primary {
    height: 48px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 500;
    letter-spacing: 2px;
    background-color: $grey-800;
    border: none;
    box-shadow: 0 2px 8px rgba($grey-950, 0.12);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

    &:hover {
      background-color: $grey-900;
      transform: translateY(-1px);
      box-shadow: 0 4px 16px rgba($grey-950, 0.15);
    }

    &:active {
      transform: translateY(0);
    }
  }

  .el-checkbox {
    .el-checkbox__label {
      color: $grey-500;
      font-size: 14px;
    }

    .el-checkbox__input.is-checked .el-checkbox__inner {
      background-color: $grey-800;
      border-color: $grey-800;
    }
  }

  .link-type {
    color: $grey-600;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;

    &:hover {
      color: $grey-900;
    }
  }
}

.login-code {
  width: 33%;
  height: 48px;
  float: right;

  img {
    cursor: pointer;
    vertical-align: middle;
    border-radius: 10px;
    height: 48px;
    border: 1px solid $grey-200;
    transition: all 0.2s ease;

    &:hover {
      border-color: $grey-400;
    }
  }
}

.el-login-footer {
  height: 40px;
  line-height: 40px;
  position: fixed;
  bottom: 0;
  width: 100%;
  text-align: center;
  color: $grey-400;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 12px;
  letter-spacing: 0.5px;
}

.login-code-img {
  height: 48px;
}
</style>
