<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <!-- 使用图标替代图片 -->
      <div class="logo">
        <el-icon class="logo-icon" :size="24"><Monitor /></el-icon>
        <span>SFpanel</span>
      </div>
      
      <el-menu
        router
        default-active="/"
        class="el-menu-vertical"
        background-color="#1d2124"
        text-color="#909399"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/file-manager">
          <el-icon><Folder /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/process-manager">
          <el-icon><List /></el-icon>
          <span>进程管理</span>
        </el-menu-item>
        <el-menu-item index="/shell-terminal">
          <el-icon><Operation /></el-icon>
          <span>Shell终端</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <el-header>
        <div class="header-left">
          <el-breadcrumb>
            <el-breadcrumb-item>首页</el-breadcrumb-item>
            <el-breadcrumb-item>仪表盘</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button type="primary" size="small">重启服务</el-button>
          <el-dropdown @command="handleCommand">
            <el-avatar size="small">Admin</el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 添加修改密码对话框 -->
  <el-dialog v-model="passwordDialog" title="修改密码" width="400px">
    <el-form :model="passwordForm" ref="passwordFormRef">
      <el-form-item label="原密码" prop="old_password">
        <el-input v-model="passwordForm.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="passwordForm.new_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认密码" prop="confirm_password">
        <el-input v-model="passwordForm.confirm_password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="passwordDialog = false">取消</el-button>
      <el-button type="primary" @click="handleChangePassword">确认</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const passwordDialog = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const handleCommand = (command) => {
  if (command === 'changePassword') {
    passwordDialog.value = true
  } else if (command === 'logout') {
    handleLogout()
  }
}

const handleChangePassword = async () => {
  try {
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
      ElMessage.error('两次输入的密码不一致')
      return
    }

    const response = await axios.post('/api/change-password', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })

    if (response.data.code === 200) {
      ElMessage.success('密码修改成功')
      passwordDialog.value = false
      // 清空表单
      passwordForm.value = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
      // 退出登录
      handleLogout()
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '密码修改失败')
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
  ElMessage.success('已退出登录')
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100vh;
}

.layout-container {
  height: 100%;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #1d2124;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  margin-right: 10px;
  color: #409EFF;
}

.logo img {
  width: 30px;
  height: 30px;
  margin-right: 10px;
}

.el-header {
  background-color: #fff;
  color: #333;
  line-height: 60px;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.el-aside {
  background-color: #1d2124;
}

.el-menu-vertical {
  height: calc(100% - 60px);
  border-right: none;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
}

.el-main {
  padding: 20px;
  background-color: #f0f2f5;
}

.el-menu-item.is-active {
  background-color: #409EFF !important;
  color: #fff !important;
}
</style>