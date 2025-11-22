import { BaseField } from './baseField';

type ButtonFormProps = {
  fieldName: string;
  fieldDescription: string;
  fieldType: string;
  fieldOnChange: (event) => void;
  fieldValue: string;
};

export function TextField({
  fieldName,
  fieldDescription,
  fieldType,
  fieldOnChange,
  fieldValue,
}: ButtonFormProps) {
  return (
    <BaseField fieldName={fieldName} fieldDescription={fieldDescription}>
      <input
        type={fieldType}
        onChange={fieldOnChange}
        value={fieldValue}
        name={fieldName}
        className="border-1 w-full"
      />
    </BaseField>
  );
}
