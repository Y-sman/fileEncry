# JwChat 聊天组件安装说明

## 安装步骤

### 方式一：通过npm安装（推荐）

如果 `jwchat` 在npm上可用，可以直接安装：

```bash
cd owl-ui
npm install jwchat -S
```

### 方式二：通过GitHub安装

如果npm上没有，可以从GitHub安装：

```bash
cd owl-ui
npm install https://github.com/jwchat/jwchat.git -S
```

或者使用yarn：

```bash
cd owl-ui
yarn add https://github.com/jwchat/jwchat.git
```

### 方式三：手动下载并引入

1. 从GitHub下载JwChat源码：https://github.com/jwchat/jwchat
2. 将源码放到 `owl-ui/src/components/jwchat` 目录
3. 在 `main.js` 中修改引入方式：

```javascript
// 改为本地引入
import Chat from '@/components/jwchat'
Vue.use(Chat)
```

## 验证安装

安装完成后，运行项目：

```bash
npm run dev
```

访问聊天页面，如果看到JwChat聊天界面，说明安装成功。

## 注意事项

1. JwChat基于Element UI，确保已安装Element UI
2. 如果遇到样式问题，可能需要引入JwChat的样式文件
3. 如果组件无法识别，检查main.js中的引入是否正确

## 备用方案

如果JwChat无法安装或使用，可以：
1. 使用其他聊天组件库（如vue-chat-scroll等）
2. 继续使用自定义的聊天组件（之前的版本）
3. 参考JwChat的设计，自己实现类似的聊天界面

