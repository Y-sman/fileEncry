<template>
  <div class="register">
    <el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form">
      <h3 class="title">文件加解密系统</h3>
      <el-form-item prop="username">
        <el-input v-model="registerForm.username" type="text" auto-complete="off" placeholder="用户名">
          <svg-icon slot="prefix" icon-class="user" class="el-input__icon input-icon" />
        </el-input>
      </el-form-item>
      <el-form-item prop="email">
        <el-input v-model="registerForm.email" type="text" auto-complete="off" placeholder="邮箱">
          <svg-icon slot="prefix" icon-class="email" class="el-input__icon input-icon" />
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="registerForm.password"
          type="password"
          auto-complete="off"
          placeholder="密码"
          @keyup.enter.native="handleRegister"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" />
        </el-input>
        <div class="pwd-tip" :class="passwordStrengthClass">
          {{ passwordStrengthText }}
        </div>
      </el-form-item>
      <el-form-item prop="confirmPassword">
        <el-input
          v-model="registerForm.confirmPassword"
          type="password"
          auto-complete="off"
          placeholder="确认密码"
          @keyup.enter.native="handleRegister"
        >
          <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" />
        </el-input>
      </el-form-item>
      <el-form-item prop="code" v-if="captchaOnOff">
        <el-input
          v-model="registerForm.code"
          auto-complete="off"
          placeholder="验证码"
          style="width: 63%"
          @keyup.enter.native="handleRegister"
        >
          <svg-icon slot="prefix" icon-class="validCode" class="el-input__icon input-icon" />
        </el-input>
        <div class="register-code">
          <img :src="codeUrl" @click="getCode" class="register-code-img"/>
        </div>
      </el-form-item>
      <el-form-item style="width:100%;">
        <el-button
          :loading="loading"
          size="medium"
          type="primary"
          style="width:100%;"
          @click.native.prevent="handleRegister"
        >
          <span v-if="!loading">注 册</span>
          <span v-else>注 册 中...</span>
        </el-button>
        <div style="float: right;">
          <router-link class="link-type" :to="'/login'">使用已有账户登录</router-link>
        </div>
      </el-form-item>
    </el-form>
    <!--  底部  -->
    <div class="el-register-footer">
    </div>
  </div>
</template>

<script>
import { getCodeImg, register } from "@/api/login";

export default {
  name: "Register",
  data() {
    const equalToPassword = (rule, value, callback) => {
      if (this.registerForm.password !== value) {
        callback(new Error("两次输入的密码不一致"));
      } else {
        callback();
      }
    };
    const passwordStrength = (rule, value, callback) => {
      if (!value) return callback();
      if (value.length < 8) {
        callback(new Error("密码至少 8 位"));
        return;
      }
      const hasLetter = /[a-zA-Z]/.test(value);
      const hasDigit = /[0-9]/.test(value);
      if (!hasLetter || !hasDigit) {
        callback(new Error("密码须同时包含字母和数字"));
        return;
      }
      callback();
    };
    return {
      codeUrl: "",
      registerForm: {
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        code: "",
        uuid: ""
      },
      registerRules: {
        username: [
          { required: true, trigger: "blur", message: "请输入用户名" },
          { min: 2, max: 20, message: "用户名长度须在 2～20 之间", trigger: "blur" }
        ],
        email: [
          { required: true, trigger: "blur", message: "请输入邮箱" },
          { type: "email", trigger: "blur", message: "请输入正确的邮箱地址" }
        ],
        password: [
          { required: true, trigger: "blur", message: "请输入密码" },
          { min: 8, max: 20, message: "密码长度须在 8～20 之间", trigger: "blur" },
          { validator: passwordStrength, trigger: "blur" }
        ],
        confirmPassword: [
          { required: true, trigger: "blur", message: "请再次输入您的密码" },
          { required: true, validator: equalToPassword, trigger: "blur" }
        ],
        code: [{ required: true, trigger: "change", message: "请输入验证码" }]
      },
      loading: false,
      captchaOnOff: true
    };
  },
  computed: {
    passwordStrengthText() {
      const pwd = this.registerForm.password || "";
      if (!pwd) return "密码强度：请输入 8-20 位，且包含字母和数字";
      if (pwd.length < 8) return "密码强度：弱（长度不足 8 位）";
      const hasLetter = /[a-zA-Z]/.test(pwd);
      const hasDigit = /[0-9]/.test(pwd);
      if (hasLetter && hasDigit) return "密码强度：合格";
      return "密码强度：弱（需同时包含字母和数字）";
    },
    passwordStrengthClass() {
      return this.passwordStrengthText.includes("合格") ? "ok" : "weak";
    }
  },
  created() {
    this.getCode();
  },
  methods: {
    getCode() {
      getCodeImg().then(res => {
        this.captchaOnOff = res.captchaOnOff === undefined ? true : res.captchaOnOff;
        if (this.captchaOnOff) {
          this.codeUrl = "data:image/gif;base64," + res.img;
          this.registerForm.uuid = res.uuid;
        }
      });
    },
    handleRegister() {
      this.$refs.registerForm.validate(valid => {
        if (valid) {
          this.loading = true;
          const payload = {
            username: this.registerForm.username,
            email: this.registerForm.email,
            password: this.registerForm.password,
            code: this.registerForm.code,
            uuid: this.registerForm.uuid
          };
          register(payload).then(res => {
            const username = this.registerForm.username;
            this.$alert("<font color='red'>恭喜你，您的账号 " + username + " 注册成功！</font>", '系统提示', {
              dangerouslyUseHTMLString: true,
              type: 'success'
            }).then(() => {
              this.$router.push("/login");
            }).catch(() => {});
          }).catch(() => {
            this.loading = false;
            if (this.captchaOnOff) {
              this.getCode();
            }
          })
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

.register {
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
    left: -300px;
    border-radius: 50%;
  }

  &::after {
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba($grey-300, 0.04) 0%, transparent 70%);
    bottom: -200px;
    right: -200px;
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

.register-form {
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
    margin-bottom: 20px;
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

.register-code {
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

.el-register-footer {
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

.register-code-img {
  height: 48px;
}

.pwd-tip {
  margin-top: 8px;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

.pwd-tip.weak {
  color: $grey-700;
  background: $grey-100;
}

.pwd-tip.ok {
  color: $grey-800;
  background: $grey-200;
}
</style>
