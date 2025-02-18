import axios from 'axios'

export const getServerStatus = () => {
  return axios.get('/api/server-status')
}

export const getProcessList = () => {
  return axios.get('/api/processes')
}

export const getFileList = () => {
  return axios.get('/api/files')
}

export const executeCommand = (command) => {
  return axios.post('/api/shell/execute', { command })
}