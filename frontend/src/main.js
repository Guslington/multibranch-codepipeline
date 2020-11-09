import Vue from 'vue'
import App from './App.vue'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import FlashMessage from '@smartweb/vue-flash-message'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(FlashMessage, {strategy: 'multiple'})

new Vue({
  render: h => h(App),
}).$mount('#app')
