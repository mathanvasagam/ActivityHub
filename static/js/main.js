(function () {
    const menuToggle = document.getElementById("menu-toggle");
    const nav = document.getElementById("main-nav");
    let lastFocusedElement = null;

    if (menuToggle && nav) {
        menuToggle.addEventListener("click", function () {
            const isOpen = nav.classList.toggle("open");
            menuToggle.setAttribute("aria-expanded", String(isOpen));
        });

        nav.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                if (!nav.classList.contains("open")) {
                    return;
                }
                nav.classList.remove("open");
                menuToggle.setAttribute("aria-expanded", "false");
            });
        });
    }

    const forms = document.querySelectorAll("form");
    forms.forEach(function (form) {
        const submitButton = form.querySelector("button[type='submit'][data-submit-label]");
        if (!submitButton) {
            return;
        }

        form.addEventListener("submit", function () {
            submitButton.dataset.loading = "true";
            submitButton.disabled = true;

            const labelNode = submitButton.querySelector("span:last-child");
            const loadingLabel = submitButton.dataset.submitLabel;
            if (labelNode && loadingLabel) {
                labelNode.textContent = loadingLabel;
            }
        });
    });

    const openButtons = document.querySelectorAll("[data-modal-open]");

    function closeModal(modal) {
        if (!modal) {
            return;
        }
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
    }

    openButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const modalId = button.getAttribute("data-modal-open");
            const modal = modalId ? document.getElementById(modalId) : null;
            if (!modal) {
                return;
            }
            modal.classList.add("open");
            modal.setAttribute("aria-hidden", "false");
        });
    });

    document.querySelectorAll("[data-modal-close]").forEach(function (button) {
        button.addEventListener("click", function () {
            const modalId = button.getAttribute("data-modal-close");
            const modal = modalId ? document.getElementById(modalId) : null;
            closeModal(modal);
        });
    });

    document.querySelectorAll(".lp-modal").forEach(function (modal) {
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                closeModal(modal);
            }
        });
    });

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") {
            return;
        }
        document.querySelectorAll(".lp-modal.open").forEach(function (modal) {
            closeModal(modal);
        });

        const createModal = document.getElementById("create-modal");
        if (createModal) {
            createModal.classList.remove("open");
            createModal.setAttribute("aria-hidden", "true");
        }

        if (nav && nav.classList.contains("open")) {
            nav.classList.remove("open");
            menuToggle && menuToggle.setAttribute("aria-expanded", "false");
        }
    });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    }

    const firebaseConfigNode = document.getElementById("firebase-web-config");
    const firebaseEmailButton = document.getElementById("firebase-email-login");
    const firebaseGoogleButton = document.getElementById("firebase-google-login");
    const firebaseSignupButton = document.getElementById("firebase-email-signup");

    if (firebaseConfigNode && (firebaseEmailButton || firebaseGoogleButton || firebaseSignupButton)) {
        const errorNode = document.getElementById("firebase-login-error");
        const signupErrorNode = document.getElementById("firebase-signup-error");
        const emailInput = document.getElementById("firebase-email");
        const passwordInput = document.getElementById("firebase-password");
        const signupEmailInput = document.getElementById("firebase-signup-email");
        const signupPasswordInput = document.getElementById("firebase-signup-password");
        const signupPassword2Input = document.getElementById("firebase-signup-password2");

        const showError = function (msg, node) {
            if (!node) {
                return;
            }
            node.hidden = false;
            node.textContent = msg;
        };

        const clearError = function (node) {
            if (node) {
                node.hidden = true;
                node.textContent = "";
            }
        };

        const setDisabled = function (disabled) {
            if (firebaseEmailButton) {
                firebaseEmailButton.disabled = disabled;
            }
            if (firebaseGoogleButton) {
                firebaseGoogleButton.disabled = disabled;
            }
        };

        const exchangeToken = async function (idToken, password) {
            const next = new URLSearchParams(window.location.search).get("next") || "/search/posts/";
            const response = await fetch("/accounts/firebase-login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ idToken: idToken, password: password || "", next: next }),
            });

            const payload = await response.json();
            if (!response.ok || !payload.ok) {
                throw new Error(payload.error || "Firebase login failed.");
            }
            window.location.href = payload.redirect || "/search/posts/";
        };

        const exchangeSignup = async function (idToken, password) {
            const next = new URLSearchParams(window.location.search).get("next") || "/search/posts/";
            const response = await fetch("/accounts/firebase-signup/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ idToken: idToken, password: password, next: next }),
            });

            const payload = await response.json();
            if (!response.ok || !payload.ok) {
                throw new Error(payload.error || "Firebase signup failed.");
            }
            window.location.href = payload.redirect || "/search/posts/";
        };

        const bootstrapFirebase = async function () {
            const config = JSON.parse(firebaseConfigNode.textContent || "{}");
            if (!config.apiKey || !config.authDomain || !config.projectId || !config.appId) {
                throw new Error("Firebase web config is incomplete.");
            }

            const firebaseModule = await import("https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js");
            const firebaseAuthModule = await import("https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js");

            const app = firebaseModule.initializeApp(config, "activityhub-web");
            const auth = firebaseAuthModule.getAuth(app);
            return { auth: auth, mod: firebaseAuthModule };
        };

        let firebaseRef = null;
        const getFirebaseRef = async function () {
            if (!firebaseRef) {
                firebaseRef = await bootstrapFirebase();
            }
            return firebaseRef;
        };

        if (firebaseEmailButton) {
            firebaseEmailButton.addEventListener("click", async function (event) {
                event.preventDefault();
                clearError(errorNode);
                setDisabled(true);
                try {
                    const identifier = (emailInput && emailInput.value || "").trim();
                    const password = (passwordInput && passwordInput.value || "").trim();
                    if (!identifier || !password) {
                        throw new Error("Enter email and password first.");
                    }

                    const loginForm = firebaseEmailButton.closest("form");
                    const looksLikeEmail = identifier.includes("@");
                    if (!looksLikeEmail) {
                        // Username login should go through normal Django auth flow.
                        if (loginForm && typeof loginForm.requestSubmit === "function") {
                            loginForm.requestSubmit();
                        } else if (loginForm) {
                            loginForm.submit();
                        }
                        return;
                    }

                    const ref = await getFirebaseRef();
                    const creds = await ref.mod.signInWithEmailAndPassword(ref.auth, identifier, password);
                    const idToken = await creds.user.getIdToken();
                    await exchangeToken(idToken, password);
                } catch (error) {
                    showError(error.message || "Firebase email login failed.", errorNode);
                    const loginForm = firebaseEmailButton.closest("form");
                    if (loginForm && typeof loginForm.requestSubmit === "function") {
                        loginForm.requestSubmit();
                        return;
                    }
                    setDisabled(false);
                }
            });
        }

        if (firebaseGoogleButton) {
            firebaseGoogleButton.addEventListener("click", async function (event) {
                event.preventDefault();
                clearError(errorNode);
                setDisabled(true);
                try {
                    const ref = await getFirebaseRef();
                    const provider = new ref.mod.GoogleAuthProvider();
                    const result = await ref.mod.signInWithPopup(ref.auth, provider);
                    const idToken = await result.user.getIdToken();
                    await exchangeToken(idToken, "");
                } catch (error) {
                    showError(error.message || "Firebase Google login failed.", errorNode);
                    setDisabled(false);
                }
            });
        }

        if (firebaseSignupButton) {
            firebaseSignupButton.addEventListener("click", async function (event) {
                event.preventDefault();
                clearError(signupErrorNode);
                setDisabled(true);
                if (firebaseSignupButton) {
                    firebaseSignupButton.disabled = true;
                }
                try {
                    const email = (signupEmailInput && signupEmailInput.value || "").trim();
                    const password = (signupPasswordInput && signupPasswordInput.value || "").trim();
                    const password2 = (signupPassword2Input && signupPassword2Input.value || "").trim();

                    if (!email || !password || !password2) {
                        throw new Error("Please fill all signup fields.");
                    }
                    if (password !== password2) {
                        throw new Error("Passwords do not match.");
                    }

                    const ref = await getFirebaseRef();
                    const creds = await ref.mod.createUserWithEmailAndPassword(ref.auth, email, password);
                    const idToken = await creds.user.getIdToken();
                    await exchangeSignup(idToken, password);
                } catch (error) {
                    showError(error.message || "Firebase signup failed.", signupErrorNode);
                    setDisabled(false);
                    if (firebaseSignupButton) {
                        firebaseSignupButton.disabled = false;
                    }
                }
            });
        }
    }

    const createModal = document.getElementById("create-modal");
    const createModalGrid = document.getElementById("create-modal-grid");
    const createModalClose = document.getElementById("create-modal-close");
    const createTriggers = [
        document.getElementById("header-create-trigger"),
        ...Array.from(document.querySelectorAll("[data-open-create-modal='true']")),
    ].filter(Boolean);

    const focusableSelector = "a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex='-1'])";

    const trapFocus = function (container, event) {
        if (!container || event.key !== "Tab") {
            return;
        }
        const focusables = Array.from(container.querySelectorAll(focusableSelector)).filter(function (el) {
            return !el.hasAttribute("disabled") && el.getAttribute("aria-hidden") !== "true";
        });
        if (!focusables.length) {
            return;
        }
        const first = focusables[0];
        const last = focusables[focusables.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            last.focus();
            event.preventDefault();
        } else if (!event.shiftKey && document.activeElement === last) {
            first.focus();
            event.preventDefault();
        }
    };

    const closeCreateModal = function () {
        if (!createModal) {
            return;
        }
        createModal.classList.remove("open");
        createModal.setAttribute("aria-hidden", "true");
        if (lastFocusedElement && typeof lastFocusedElement.focus === "function") {
            lastFocusedElement.focus();
        }
    };

    const renderCreateOptions = function (options) {
        if (!createModalGrid) {
            return;
        }
        createModalGrid.innerHTML = "";
        options.forEach(function (option) {
            const card = document.createElement("a");
            card.className = "create-option";
            card.href = option.href;

            const title = document.createElement("strong");
            title.textContent = option.label;

            const desc = document.createElement("p");
            desc.textContent = option.description;

            const cta = document.createElement("span");
            cta.textContent = "Open " + option.label + " form";

            card.appendChild(title);
            card.appendChild(desc);
            card.appendChild(cta);
            createModalGrid.appendChild(card);
        });
    };

    const openCreateModal = async function () {
        if (!createModal || !createModalGrid) {
            return;
        }

        lastFocusedElement = document.activeElement;

        createModal.classList.add("open");
        createModal.setAttribute("aria-hidden", "false");
        createModalGrid.innerHTML = "<p class='muted'>Loading options...</p>";
        if (createModalClose) {
            createModalClose.focus();
        }

        try {
            const response = await fetch("/search/create-options/", {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });
            const payload = await response.json();
            if (!response.ok || !payload.ok || !Array.isArray(payload.options)) {
                throw new Error(payload.error || "Failed to load create options.");
            }
            renderCreateOptions(payload.options);
        } catch (error) {
            createModalGrid.innerHTML = "<p class='field-error'>" + (error.message || "Unable to load options.") + "</p>";
        }
    };

    createTriggers.forEach(function (trigger) {
        trigger.addEventListener("click", function () {
            openCreateModal();
        });
    });

    if (createModalClose) {
        createModalClose.addEventListener("click", closeCreateModal);
    }

    if (createModal) {
        createModal.addEventListener("click", function (event) {
            if (event.target === createModal) {
                closeCreateModal();
            }
        });

        createModal.addEventListener("keydown", function (event) {
            trapFocus(createModal, event);
        });
    }

})();
