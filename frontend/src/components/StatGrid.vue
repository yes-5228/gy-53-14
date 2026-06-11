<script setup>
defineProps({
  stats: {
    type: Array,
    required: true,
  },
  areaRanking: {
    type: Array,
    default: () => [],
  },
});

function getTensionLevel(idleRate) {
  if (idleRate <= 20) return "critical";
  if (idleRate <= 40) return "high";
  if (idleRate <= 60) return "medium";
  return "low";
}
</script>

<template>
  <div class="ranking-panel">
    <div class="ranking-header">
      <h3>区域空闲率排行</h3>
      <span class="ranking-hint">按空闲率从低到高排列，红色标识紧张车区</span>
    </div>
    <div class="ranking-grid">
      <section
        v-for="(area, index) in areaRanking"
        :key="area.area"
        class="ranking-card"
        :class="`tension-${getTensionLevel(area.idle_rate)}`"
      >
        <div class="ranking-top">
          <div class="ranking-badge" :class="`rank-${index + 1}`">{{ index + 1 }}</div>
          <div class="ranking-info">
            <strong>{{ area.area }}</strong>
            <span>空闲 {{ area.free }} / 共 {{ area.total }}</span>
          </div>
          <div class="ranking-rate" :class="`tension-${getTensionLevel(area.idle_rate)}`">
            <strong>{{ area.idle_rate }}%</strong>
            <span>空闲率</span>
          </div>
        </div>
        <div class="progress-bar">
          <div
            class="progress-fill"
            :class="`tension-${getTensionLevel(area.idle_rate)}`"
            :style="{ width: `${area.idle_rate}%` }"
          ></div>
        </div>
        <div class="ranking-stats">
          <span class="stat-item"><em class="dot-occupied"></em>占用 {{ area.occupied }}</span>
          <span class="stat-item"><em class="dot-reserved"></em>预约 {{ area.reserved }}</span>
          <span class="stat-item"><em class="dot-maintenance"></em>维护 {{ area.maintenance }}</span>
        </div>
      </section>
    </div>
    <div class="stat-grid">
      <section v-for="item in stats" :key="item.label" class="stat-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </section>
    </div>
  </div>
</template>
