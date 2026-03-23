import { useMemo } from 'react'
import type { DistributionSchema, IntDistribution, ParamSchema } from '@/api/types'
import { Input } from './Input'
import { Select } from './Select'

interface DistributionInputProps {
  value: IntDistribution
  onChange: (value: IntDistribution) => void
  schemas: DistributionSchema[]
  className?: string
}

function parseParamValue(param: ParamSchema, raw: string): number {
  if (param.type === 'int') return Number.parseInt(raw || '0', 10)
  return Number.parseFloat(raw || '0')
}

export function DistributionInput({ value, onChange, schemas, className }: DistributionInputProps) {
  const schema = useMemo(
    () => schemas.find((s) => s.type === value.type),
    [schemas, value.type],
  )

  const typeOptions = useMemo(
    () => schemas.map((s) => ({ value: s.type, label: s.label })),
    [schemas],
  )

  return (
    <div className={className}>
      <Select
        label="Distribution"
        value={value.type}
        onValueChange={(type) => {
          const newSchema = schemas.find((s) => s.type === type)
          const params: Record<string, number> = {}
          for (const p of newSchema?.params ?? []) {
            params[p.name] = p.default as number
          }
          onChange({ type: type as IntDistribution['type'], params })
        }}
        options={typeOptions}
      />
      {schema?.params.map((param) => (
        <Input
          key={param.name}
          label={param.label}
          type="number"
          step={param.type === 'float' ? '0.1' : '1'}
          min={param.min}
          max={param.max}
          value={String(value.params[param.name] ?? param.default)}
          onChange={(e) =>
            onChange({
              ...value,
              params: { ...value.params, [param.name]: parseParamValue(param, e.target.value) },
            })
          }
          className="mt-1.5"
        />
      ))}
    </div>
  )
}
