<template>
  <!-- Mirrors the real result-row geometry so nothing jumps when data lands. -->
  <div class="flex gap-3 items-center px-4 py-3 animate-pulse">
    <div class="w-11 h-[62px] rounded bg-slate-800/80 flex-none"></div>
    <div class="flex-1 flex flex-col gap-2">
      <div class="h-3 rounded bg-slate-800" :style="{ width: titleWidth }"></div>
      <div class="h-2.5 rounded bg-slate-800/60" :style="{ width: metaWidth }"></div>
    </div>
    <div class="w-20 h-8 rounded-md bg-slate-800/60 flex-none"></div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonRow',
  props: {
    titleWidth: { type: String, default: '65%' },
    metaWidth: { type: String, default: '40%' },
  },
}
</script>
