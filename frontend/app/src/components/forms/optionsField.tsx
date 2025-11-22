import { BaseField } from './baseField';

export function SelectField({
  fieldName,
  fieldDescription,
  fieldOptions,
  fieldOnChange,
  fieldValue,
}) {
  return (
    <BaseField fieldName={fieldName} fieldDescription={fieldDescription}>
      <select value={fieldValue} onChange={fieldOnChange} name={fieldName}>
        <option value={''}> Select an option: </option>
        {fieldOptions.map((item, index) => (
          <option key={index} value={item.value}>
            {item.name}
          </option>
        ))}
      </select>
    </BaseField>
  );
}
