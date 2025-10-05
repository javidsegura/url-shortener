import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "../../../../firebase";
import { config } from "@/core/config";

export function GoogleAuthButton() {
  const handleRegisterWithGoogle = async (event) => {
    event.preventDefault();

    try {
      const provider = new GoogleAuthProvider();
      const userCredentials = await signInWithPopup(auth, provider);
      const user = userCredentials.user;
      console.log("User signed up:", user);

      const dbResponse = await fetch(new URL("user", config.BASE_API_URL).href, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: user.uid,
          displayable_name: user.displayName,
          email: user.email,
          country: "ES",
          profile_pic_object_name: user.photoURL,
        }),
      });

      if (!dbResponse.ok) {
        throw new Error("An error occurred while storing user info.");
      }
    } catch (error) {
      console.error("Error occurred:", error.message);
    }
  };

  return (
    <button
      onClick={handleRegisterWithGoogle}
      className="flex items-center justify-center gap-3 w-full py-3 px-4 mt-3 border border-gray-300 rounded-lg shadow-sm bg-white hover:bg-gray-50 transition-colors duration-200 text-gray-700 font-medium text-sm active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300"
    >
      {/* Inline Google G logo */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        width="20px"
        height="20px"
      >
        <path
          fill="#FFC107"
          d="M43.6 20.5H42V20H24v8h11.3C33.9 32.3 29.4 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.7 1.1 7.8 3l5.7-5.7C33.5 6.4 28.9 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20c11 0 19-8 19-20 0-1.3-.1-2.5-.4-3.5z"
        />
        <path
          fill="#FF3D00"
          d="M6.3 14.7l6.6 4.8C14.2 16.3 18.7 12 24 12c3 0 5.7 1.1 7.8 3l5.7-5.7C33.5 6.4 28.9 4 24 4c-7.9 0-14.5 4.6-17.7 10.7z"
        />
        <path
          fill="#4CAF50"
          d="M24 44c5.3 0 10-1.8 13.6-4.9l-6.3-5.2C29.1 35.3 26.6 36 24 36c-5.4 0-9.9-3.7-11.6-8.8l-6.6 5C9.5 39.1 16.2 44 24 44z"
        />
        <path
          fill="#1976D2"
          d="M43.6 20.5H42V20H24v8h11.3c-1.1 3.3-3.6 6-6.7 7.6l6.3 5.2C38 37.2 43.6 31.5 43.6 20.5z"
        />
      </svg>

      <span>Continue with Google</span>
    </button>
  );
}
