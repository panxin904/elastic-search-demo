import { ref } from 'vue'
import graphDataRaw from '../graph.json'

export function useGraphData() {
  const graphData = ref<any>(graphDataRaw)
  const loaded = ref(true)

  return {
    graphData,
    loaded
  }
}
