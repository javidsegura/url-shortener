import { BaseField } from './baseField';

export function FileField({
  fieldName,
  fieldDescription,
  multiple,
  accept,
  fieldOnChange,
}) {
  return (
    <BaseField fieldName={fieldName} fieldDescription={fieldDescription}>
      <input
        type="file"
        accept={accept}
        onChange={fieldOnChange}
        name={fieldName}
      />
    </BaseField>
  );
}
