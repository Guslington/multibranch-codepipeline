<template>
  <div id="app">
    <NavBar/>
    <Repos/>
    <FlashMessage :position="'right bottom'"></FlashMessage>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'
import Repos from './components/Repos.vue'

export default {
  name: 'App',
  components: {
    NavBar, Repos
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
