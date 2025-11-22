import { useState } from 'react';

export const useForm = (initialState) => {
  const [formData, setFormData] = useState(initialState);

  const handleFormChange = (event) => {
    const { name, value, type, checked, files } = event.target;

    let fieldvalue;

    switch (type) {
      case 'file':
        fieldvalue = files[0];
        break;
      default:
        fieldvalue = value;
    }

    setFormData((prevData) => ({
      ...prevData,
      [name]: fieldvalue,
    }));
  };

  return [formData, handleFormChange];
};
