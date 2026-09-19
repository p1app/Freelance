import { reactive } from 'vue'

// Единое состояние диалога подтверждения (компонент ConfirmDialog монтируется в App.vue)
const state = reactive({
    visible: false,
    title: '',
    text: '',
    confirmText: 'Подтвердить',
    cancelText: 'Отмена',
    color: 'primary',
    resolve: null,
})

/**
 * Замена нативному confirm(): возвращает Promise<boolean>.
 * Использование: if (!(await confirm({ title: 'Удалить?' }))) return
 */
export function useConfirm() {
    function confirm({
        title,
        text = '',
        confirmText = 'Подтвердить',
        cancelText = 'Отмена',
        color = 'primary',
    }) {
        state.title = title
        state.text = text
        state.confirmText = confirmText
        state.cancelText = cancelText
        state.color = color
        state.visible = true

        return new Promise((resolve) => {
            state.resolve = resolve
        })
    }

    function answer(value) {
        state.visible = false
        if (state.resolve) {
            state.resolve(value)
            state.resolve = null
        }
    }

    return { state, confirm, answer }
}
