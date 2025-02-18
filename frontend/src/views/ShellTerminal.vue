<template>
  <div class="shell-terminal">
    <el-card>  <!-- Element Plus 的卡片组件，提供了一个带边框的容器 -->
      <template #header>  <!-- 卡片的头部插槽 -->
        <div class="card-header">Shell终端</div>
      </template>
      
      <!-- 终端输出区域，显示命令执行的结果 -->
      <div class="terminal-output">{{ output }}</div>
      
      <!-- 命令输入框，支持回车执行命令 -->
      <el-input
        v-model="command"
        placeholder="输入命令"
        @keyup.enter="executeCommand"
      >
        <!-- 在输入框后面添加执行按钮 -->
        <template #append>
          <el-button @click="executeCommand">执行</el-button>
        </template>
      </el-input>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const command = ref('')
const output = ref('')

const executeCommand = async () => {
  if (!command.value) return
  
  try {
    const response = await axios.post('http://localhost:5000/api/shell/execute', {
      command: command.value
    })
    if (response.data.code === 200) {
      output.value += `\n$ ${command.value}\n${response.data.data}`
      command.value = ''
    }
  } catch (error) {
    console.error('执行命令失败:', error)
  }
}
</script>

<style scoped>
.terminal-output {
  background: #1e1e1e;
  color: #fff;
  padding: 10px;
  margin-bottom: 10px;
  min-height: 300px;
  font-family: monospace;
  white-space: pre-wrap;
}
</style>