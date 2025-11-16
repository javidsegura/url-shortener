import { useState, useMemo } from "react";
import { auth } from "../../../firebase";
import {
  createUserWithEmailAndPassword,
  sendEmailVerification,
  updateProfile,
} from "firebase/auth";
import { SelectField } from "../forms/optionsField";
import { TextField } from "../forms/textField";
import { FileField } from "../forms/fileField";

import { COUNTRIES_LIST } from "../../data/countries";
import { useForm } from "../../hooks/useForm";
import { config } from "../../core/config";

export default function RegisterForm() {
  const [formContent, handleFormChangeRaw] = useForm({
    name: "",
    email: "",
    password: "",
    country: "",
    profile_pic: "", // File object (required)
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generalError, setGeneralError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // ---------- Validation ----------
  const validate = (values) => {
    const e = {};

    // Name
    if (!values.name?.trim()) e.name = "Name is required.";
    else if (values.name.trim().length < 2) e.name = "Name must be at least 2 characters.";

    // Email
    if (!values.email?.trim()) e.email = "Email is required.";
    else {
      const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRe.test(values.email.trim())) e.email = "Please enter a valid email.";
    }

    // Password
    if (!values.password) e.password = "Password is required.";
    else {
      if (values.password.length < 8) e.password = "Minimum 8 characters.";
      const hasLetter = /[A-Za-z]/.test(values.password);
      const hasNumber = /\d/.test(values.password);
      if (!(hasLetter && hasNumber)) {
        e.password = (e.password ? e.password + " " : "") + "Include letters and numbers.";
      }
    }

    // Country
    if (!values.country) e.country = "Please select a country.";

    // Profile pic (REQUIRED)
    const file = values.profile_pic;
    if (!file) e.profile_pic = "Profile picture is required.";
    else {
      if (!file.type?.startsWith("image/")) e.profile_pic = "File must be an image.";
      const MAX_MB = 5;
      if (file.size > MAX_MB * 1024 * 1024) e.profile_pic = `Image must be under ${MAX_MB}MB.`;
    }

    return e;
  };

  const currentErrors = useMemo(() => validate(formContent), [formContent]);
  const isFormValid = Object.keys(currentErrors).length === 0;

  // Wrap original onChange to mark touched & keep errors fresh
  const handleFormChange = (name, value) => {
    handleFormChangeRaw(name, value);
    setTouched((t) => ({ ...t, [name]: true }));
    setErrors(validate({ ...formContent, [name]: value }));
    setGeneralError("");
    setSuccessMsg("");
  };

  const handleBlur = (name) => {
    setTouched((t) => ({ ...t, [name]: true }));
    setErrors(validate(formContent));
  };

  // ---------- Submit ----------
  const handleRegisterWithEmail = async (event) => {
    event.preventDefault();
    setGeneralError("");
    setSuccessMsg("");

    // surface all errors
    setTouched({
      name: true,
      email: true,
      password: true,
      country: true,
      profile_pic: true,
    });
    setErrors(validate(formContent));

    if (!isFormValid) return;

    setIsSubmitting(true);

    let file_path = null;

    try {
      // (1) Get presigned URL & upload profile pic (mandatory)
      const preSignedUrlResponse = await fetch(
        new URL("user/profile_pic", config.BASE_API_URL).href,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            file_name: formContent.profile_pic.name,
            content_type: formContent.profile_pic.type,
          }),
        }
      );

      if (!preSignedUrlResponse.ok) {
        const txt = await preSignedUrlResponse.text();
        throw new Error(txt || "Failed to get upload URL.");
      }

      const data = await preSignedUrlResponse.json();
      const presigned_url = data.presigned_url;
      file_path = data.file_path;

      const fileUploadResponse = await fetch(presigned_url, {
        method: "PUT",
        body: formContent.profile_pic,
        headers: { 
          "Content-Type": formContent.profile_pic.type ,
          "x-ms-blob-type": "BlockBlob",
      },
      });

      if (!fileUploadResponse.ok) {
        const txt = await fileUploadResponse.text();
        throw new Error(txt || "Failed to upload file.");
      }

      // (2) Register user with Firebase
      const userCredentials = await createUserWithEmailAndPassword(
        auth,
        formContent.email,
        formContent.password
      );

      await sendEmailVerification(userCredentials.user);

      await updateProfile(userCredentials.user, {
        displayName: formContent.name,
        // If you also mirror the photoURL to Firebase (optional):
        // photoURL: s3_public_url  // only if your backend returns a public URL
      });

      // (3) Store user in your DB
      const db_response = await fetch(new URL("user", config.BASE_API_URL).href, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userCredentials.user.uid,
          displayable_name: formContent.name,
          email: formContent.email,
          country: formContent.country,
          profile_pic_object_name: file_path, // required & present
        }),
      });

      if (!db_response.ok) {
        const txt = await db_response.text();
        throw new Error(txt || "Failed to persist user.");
      }

      setSuccessMsg("Account created! Please check your email to verify your address.");
    } catch (error) {
      console.error("Signup error:", error?.message || error);
      setGeneralError(
        "Something went wrong while creating your account. Please review your info and try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // ---------- Fields (with errors & a11y) ----------
  const fields = [
    {
      Component: TextField,
      key: "name",
      props: {
        fieldName: "name",
        fieldDescription: "Your full name",
        fieldType: "text",
        fieldOnChange: handleFormChange,
        fieldValue: formContent.name,
        fieldOnBlur: () => handleBlur("name"),
        "aria-invalid": !!(touched.name && currentErrors.name),
        "aria-describedby": touched.name && currentErrors.name ? "error-name" : undefined,
      },
      error: touched.name && currentErrors.name,
    },
    {
      Component: TextField,
      key: "email",
      props: {
        fieldName: "email",
        fieldDescription: "We'll send a verification link",
        fieldType: "email",
        fieldOnChange: handleFormChange,
        fieldValue: formContent.email,
        fieldOnBlur: () => handleBlur("email"),
        "aria-invalid": !!(touched.email && currentErrors.email),
        "aria-describedby": touched.email && currentErrors.email ? "error-email" : undefined,
      },
      error: touched.email && currentErrors.email,
    },
    {
      Component: TextField,
      key: "password",
      props: {
        fieldName: "password",
        fieldDescription: "Min 8 chars, include letters & numbers",
        fieldType: "password",
        fieldOnChange: handleFormChange,
        fieldValue: formContent.password,
        fieldOnBlur: () => handleBlur("password"),
        "aria-invalid": !!(touched.password && currentErrors.password),
        "aria-describedby":
          touched.password && currentErrors.password ? "error-password" : undefined,
      },
      error: touched.password && currentErrors.password,
    },
    {
      Component: SelectField,
      key: "country",
      props: {
        fieldName: "country",
        fieldDescription: "Select your country",
        fieldOptions: COUNTRIES_LIST,
        fieldOnChange: handleFormChange,
        fieldValue: formContent.country,
        fieldOnBlur: () => handleBlur("country"),
        "aria-invalid": !!(touched.country && currentErrors.country),
        "aria-describedby":
          touched.country && currentErrors.country ? "error-country" : undefined,
      },
      error: touched.country && currentErrors.country,
    },
    {
      Component: FileField,
      key: "profile_pic",
      props: {
        fieldName: "profile_pic",
        fieldDescription: "Upload a profile photo (required)",
        multiple: false,
        accept: "image/*",
        fieldOnChange: handleFormChange,
        fieldOnBlur: () => handleBlur("profile_pic"),
        "aria-invalid": !!(touched.profile_pic && currentErrors.profile_pic),
        "aria-describedby":
          touched.profile_pic && currentErrors.profile_pic ? "error-profile_pic" : undefined,
      },
      error: touched.profile_pic && currentErrors.profile_pic,
    },
  ];

  return (
    <form
      onSubmit={handleRegisterWithEmail}
      className="w-full max-w-md mx-auto bg-white border border-gray-200 rounded-2xl shadow-lg p-6 space-y-5"
    >
      <div className="space-y-1 text-center">
        <h2 className="text-2xl font-semibold text-gray-900">Create your account</h2>
        <p className="text-sm text-gray-500">It only takes a minute.</p>
      </div>

      {/* Success */}
      {successMsg ? (
        <div
          className="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800"
          role="status"
        >
          {successMsg}
        </div>
      ) : null}

      {/* General error */}
      {generalError ? (
        <div
          className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
          role="alert"
        >
          {generalError}
        </div>
      ) : null}

      {/* Field errors summary (optional but helpful) */}
      {Object.keys(currentErrors).length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          Please fix the errors below.
          <ul className="list-disc pl-5 mt-1">
            {Object.entries(currentErrors).map(([k, v]) => (
              <li key={k}>{v}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="space-y-3">
        {fields.map(({ Component, key, props, error }) => (
          <div key={key} className="space-y-1">
            <Component {...props} />
            {error ? (
              <p id={`error-${key}`} className="text-xs text-red-600">
                {error}
              </p>
            ) : null}
          </div>
        ))}
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !isFormValid}
        className={`w-full inline-flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition
          ${
            isSubmitting || !isFormValid
              ? "bg-gray-200 text-gray-500 cursor-not-allowed"
              : "bg-gray-900 text-white hover:bg-gray-800 active:scale-[0.99]"
          }`}
      >
        {isSubmitting ? (
          <>
            <svg
              className="h-4 w-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4A4 4 0 008 12H4z"
              />
            </svg>
            Creating account…
          </>
        ) : (
          "Create account"
        )}
      </button>

      <p className="text-[11px] text-gray-500 text-center">
        By continuing, you agree to our Terms & Privacy Policy.
      </p>
    </form>
  );
}
