export function BaseField({ children, fieldName, fieldDescription }) {
  return (
    <label>
      <div className="flex flex-col">
        <p> {fieldName}: </p>
        <i className="text-xs"> {fieldDescription}</i>
      </div>
      {children}
    </label>
  );
}
