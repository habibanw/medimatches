describe("Profile", () => {
    beforeEach(() => {
      cy.visit("/logout")
      cy.visit("/login")
    })
    it("Should update provider profile form", () => {
        cy.fixture("provider").then((provider) => {

            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password, { log: false })
            cy.get("#id_submit").click()

            cy.visit("/provider_update")
            cy.get("h1").contains("Welcome TAMMY")
            cy.get("#id_provider_id").should("have.value", "1114033073")
            cy.get("#id_facility_name").clear().type("Test")
            cy.get("#id_submit").click()

            cy.get("#id_facility_name").should("have.value", "Test")
            cy.get('.success').contains("Updates saved successfully")

        })
    })
    it("Should not allow non-provider users to access profile form", () => {
        cy.fixture("patient").then((patient) => {

            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            cy.visit("/provider_update")
            cy.get('.error').contains("You do not have access to this page")

        })
    })
    it("Should not allow unauthenticated users to access profile form", () => {
        cy.fixture("unregistered").then((unregistered) => {

            cy.get("#id_email").type(unregistered.username)
            cy.get("#id_password").type(unregistered.password, { log: false })
            cy.get("#id_submit").click()

            cy.visit("/provider_update")
            cy.get('.error').contains("You must log in to update your profile")

        })
    })
})