import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import FolderUpload from '../components/FolderUpload.vue'
import PaperVisualization from '../components/PaperVisualization.vue'

const routes = [
  {
    path: '/',
    redirect: '/upload'
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/upload',
    name: 'FolderUpload',
    component: FolderUpload
  },
  {
    path: '/visualization',
    name: 'PaperVisualization',
    component: PaperVisualization
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
