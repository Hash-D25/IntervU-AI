"use client";

import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import type { ReactNode } from "react";

import { env } from "@/env";

type GoogleAuthProviderProps = {
  children: ReactNode;
};

export function GoogleAuthProvider({ children }: GoogleAuthProviderProps) {
  if (!env.googleClientId) {
    return children;
  }

  return <GoogleOAuthProvider clientId={env.googleClientId}>{children}</GoogleOAuthProvider>;
}

type GoogleSignInButtonProps = {
  disabled?: boolean;
  onSuccess: (idToken: string) => void | Promise<void>;
  onError: () => void;
};

export function GoogleSignInButton({ disabled, onSuccess, onError }: GoogleSignInButtonProps) {
  if (!env.googleClientId) {
    return null;
  }

  return (
    <div className="flex justify-center">
      <GoogleLogin
        onSuccess={(response) => {
          if (response.credential) {
            void onSuccess(response.credential);
          } else {
            onError();
          }
        }}
        onError={onError}
        theme="filled_black"
        size="large"
        text="continue_with"
        shape="rectangular"
        width={320}
        useOneTap={false}
        containerProps={{
          className: disabled ? "pointer-events-none opacity-50" : undefined,
        }}
      />
    </div>
  );
}
