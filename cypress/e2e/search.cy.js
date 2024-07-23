describe('Visit the provider list', () => {

    it("gets search results for name", () => {
      cy.visit("/providers") // Arrange
      
      
      cy.get("#id_name_query").type("TAMMY", { log: false })
      cy.get("#id_gender").select("Female")
      cy.get("#id_search").click()

      cy.get("ul.listing").find("li").should('have.length', 50)
    
      cy.contains('.listing li', 'ABBOTT, TAMMY').should('be.visible')
      cy.contains('.listing li', 'NURSE PRACTITIONER, AUBURN, ME, 042106334, ST MARYS REGIONAL MEDICAL CENTER').should('be.visible')
    })

    it("gets search results for city, gender, name, and state", () => {
      cy.visit("/providers") // Arrange
      
      cy.get("#id_name_query").type("Benjamin", { log: false })
      cy.get("#id_city").type("watertown")
      cy.get("#id_gender").select("Male")
      cy.get("#id_state").select("SD")
      cy.get("#id_search").click()
      cy.contains('#id_total_providers', '1 providers').should('be.visible')
      cy.get("ul.listing").find("li").should('have.length', 1)
      cy.contains('.listing li', 'AAKER, BENJAMIN').should('be.visible')
      cy.contains('.listing li', 'EMERGENCY MEDICINE, WATERTOWN, SD, 572011548, PRAIRIE LAKES HEALTH CARE SYSTEMS INC').should('be.visible')
  })

  it("gets search results for zip code w 5 digits -- CAN FAIL IF API IS NOT WORKING", () => {
    cy.visit("/providers") // Arrange
    
    cy.get("#id_zip_code").type("43551", { log: false })
    cy.get("#id_search").click()

    cy.contains('#id_total_providers', '2,352 providers').should('be.visible')
    cy.get("ul.listing").find("li").should('have.length', 50)
    cy.contains('.listing li', 'ACKERMAN SPAIN, KAREN').should('be.visible')
    cy.contains('.listing li', 'CLINICAL PSYCHOLOGIST, PERRYSBURG, OH, 435515228, ').should('be.visible')

})

  it("does a full-text search from the homepage", () => {
    cy.visit("/") // Arrange
  
    cy.get(".fulltext-search input").type("TAMMY", { log: false })
    cy.get("#fulltext-search-submit").click()

    cy.contains('#id_total_providers', '975 providers').should('be.visible')
    cy.get("ul.listing").find("li").should('have.length', 50)
    cy.contains('.listing li', 'TAMMY').should('be.visible')
  })

  it("does a full-text search from the homepage and then does field searches on provider list page", () => {
    cy.visit("/") // Arrange
  
    cy.get(".fulltext-search input").type("TAMMY", { log: false })
    cy.get("#fulltext-search-submit").click()

    cy.get("#id_city").type("Arlington", { log: false })

    cy.get("#id_search").click()

    cy.contains('#id_total_providers', '3 providers').should('be.visible')
    cy.get("ul.listing").find("li").should('have.length', 3)
    cy.contains('.listing li', 'NOVAK, TAMMY').should('be.visible')
  })
})