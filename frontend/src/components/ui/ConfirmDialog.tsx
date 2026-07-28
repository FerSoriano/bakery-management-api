import { Button } from './Button'
import { Modal } from './Modal'

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirmar',
  pending = false,
  onConfirm,
  onCancel,
}: {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  pending?: boolean
  onConfirm: () => void
  onCancel: () => void
}) {
  return (
    <Modal
      open={open}
      title={title}
      onClose={onCancel}
      footer={
        <>
          <Button onClick={onCancel} disabled={pending}>
            Cancelar
          </Button>
          <Button variant="danger" onClick={onConfirm} disabled={pending}>
            {pending ? 'Procesando…' : confirmLabel}
          </Button>
        </>
      }
    >
      <p className="text-sm text-stone-600">{message}</p>
    </Modal>
  )
}
